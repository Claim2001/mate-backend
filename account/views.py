import io
import re
import pycurl
from urllib.parse import urlencode

from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveUpdateAPIView, GenericAPIView, DestroyAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
from rest_framework_jwt.settings import api_settings

from account.models import UserModel, TokenModel, ProfileModel
from account.permissions import HighPermission, AdminPermission
from account.serializers import RegistrationTokenSerializer, PasswordForgetCodeSerializer, ProfileSerializer, \
    RegistrationSerializer, UserDABSerializer, RegistrationForgetTokenSerializer
from account.utils import send_sms_code, generate_code
from courses.models import UserBoughtCourseModel
from dashboard.models import NotificationModel


@api_view(('GET', 'POST'))
def logout_user(request):
    logout(request)
    response = Response({'message': 'Successfully logout'},
                        status=status.HTTP_200_OK)
    response.delete_cookie('Auth')
    return response


class RegistrationView(GenericAPIView):
    """Registration of new User
    POST:
    {
        username: string,
        password1: string,
        password2 string,
    }
    If passwords aren`t same returns: Passwords should be the same
    If user is already created returns: User with this phone has been already created
    If user account is not activated: User account is disabled
    If success: 'User was created successfully'
    If phone format incorrect: Incorrect phone number format
    """
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        username = data['username']
        phone = data['phone'].replace("+", "").replace("-", "").replace(" ", "")
        email = data['email']
        errors = {}
        exists = User.objects.filter(username=username, profile__phone=phone, email=email)
        if exists.exists():
            if exists.get().is_active:
                return Response({'message': 'User with this username/phone/mail has been already created'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                code = generate_code()
                user = UserModel.objects.get(username=username, profile__phone=phone, is_active=False,
                                             email=data['email'])
                TokenModel.objects.filter(user=user).delete()
                TokenModel.objects.create(user=user, code=code)
                send_sms_code(phone, code)
                b = io.BytesIO()
                sms = pycurl.Curl()
                sms.setopt(sms.URL, 'http://185.8.212.184/smsgateway/')
                adddata = '[{"phone": "%s", "text": "Ваш код для MATE LMS: %d. Sizning MATE LMS kodi: %d"}]' % (
                    phone, code, code)
                payload = {'login': 'ITACADEMY', 'password': 'udYZ8fu5w8QwDA4592pe', 'data': adddata}
                payload = urlencode(payload)
                sms.setopt(sms.HEADER, 0)
                sms.setopt(sms.POST, 1)
                sms.setopt(sms.CONNECTTIMEOUT, 8)
                sms.setopt(sms.TIMEOUT, 8)
                sms.setopt(sms.SSL_VERIFYPEER, False)
                sms.setopt(sms.SSL_VERIFYHOST, 0)
                sms.setopt(sms.POSTFIELDS, payload)
                sms.setopt(sms.USERAGENT, 'Opera 10.00')
                sms.setopt(sms.WRITEFUNCTION, b.write)
                sms.perform()
                sms.close()
            return Response({'message': f'User account is not activated, new code has been sent'},
                            status=status.HTTP_200_OK)
        if User.objects.filter(username=username).exists():
            return Response({'message': 'User with this username has been already created'},
                            status=status.HTTP_400_BAD_REQUEST)
        elif User.objects.filter(profile__phone=phone).exists():
            return Response({'message': 'User with this phone has been already created'},
                            status=status.HTTP_400_BAD_REQUEST)
        elif User.objects.filter(email=email).exists():
            return Response({'message': 'User with this mail has been already created'},
                            status=status.HTTP_400_BAD_REQUEST)
        if data['password1'] != data['password2']:
            errors['password2'] = {'Passwords should be the same'}
        if re.match(r'^998\d{9}$', phone):
            code = generate_code()
            user = UserModel.objects.create(username=username, first_name=data['first_name'],
                                            last_name=data['last_name'], is_active=False, email=data['email'])
            user.set_password(data['password1'])
            user.save()
            TokenModel.objects.create(user=user, code=code)
            ProfileModel.objects.create(user=user, dob=data['dob'], gender=data['gender'], permission=0, phone=phone)
            b = io.BytesIO()
            sms = pycurl.Curl()
            sms.setopt(sms.URL, 'http://185.8.212.184/smsgateway/')
            adddata = '[{"phone": "%s", "text": "Ваш код для MATE LMS: %d. Sizning MATE LMS kodi: %d"}]' % (
                phone, code, code)
            payload = {'login': 'ITACADEMY', 'password': 'udYZ8fu5w8QwDA4592pe', 'data': adddata}
            payload = urlencode(payload)
            sms.setopt(sms.HEADER, 0)
            sms.setopt(sms.POST, 1)
            sms.setopt(sms.CONNECTTIMEOUT, 8)
            sms.setopt(sms.TIMEOUT, 8)
            sms.setopt(sms.SSL_VERIFYPEER, False)
            sms.setopt(sms.SSL_VERIFYHOST, 0)
            sms.setopt(sms.POSTFIELDS, payload)
            sms.setopt(sms.USERAGENT, 'Opera 10.00')
            sms.setopt(sms.WRITEFUNCTION, b.write)
            sms.perform()
            sms.close()
            return Response({'message': f'User was created successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Wrong phone format'}, status=status.HTTP_200_OK)


class RegistrationTokenView(GenericAPIView):
    """Endpoint for validating token sent to the user Returns:
        if code is valid:
        {
            "token": "some token"
        }
        if not:
        {
            "message": "Code is incorrect",
            "status": false
        }
    """
    serializer_class = RegistrationTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        code = data['code']
        phone = data['phone'].replace("+", "").replace("-", "").replace(" ", "")
        token = TokenModel.objects.filter(code=code, user__profile__phone=phone)
        if not token.exists():
            return Response({'message': 'Code is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
        time_diff = (timezone.now() - token.get().created_at).total_seconds() / 60
        if time_diff > 5:
            return Response({'message': 'Code is expired'}, status=status.HTTP_400_BAD_REQUEST)
        user = token.get().user
        user.is_active = True
        user.save()
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        TokenModel.objects.filter(user=user).delete()
        data = {'token': token,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'phone': user.profile.phone,
                'permission': user.profile.get_permission_display(),
                'used_trial': user.profile.used_trial,
                "notifications": NotificationModel.objects.filter(seen=False, to_user=user).count()}
        if not user.profile.avatar:
            data["avatar"] = None
        else:
            data["avatar"] = request.build_absolute_uri(user.profile.avatar.url)
        response = Response(data, status=status.HTTP_201_CREATED)
        expiration = (timezone.now() + api_settings.JWT_EXPIRATION_DELTA)
        response.set_cookie(api_settings.JWT_AUTH_COOKIE, token, expires=expiration, httponly=True, secure=True)
        return response


class PasswordForgetCodeView(GenericAPIView):
    """Forget password
    Args:
        phone
    Returns:
        phone
    """
    serializer_class = PasswordForgetCodeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            data = serializer.validated_data
            phone = data['phone'].replace("+", "").replace("-", "").replace(" ", "")
            matched = re.match(r'^998\d{9}$', phone)
            if matched:
                user = UserModel.objects.filter(profile__phone=phone)
                if user.exists():
                    code = generate_code()
                    TokenModel.objects.filter(user=user.get()).delete()
                    TokenModel.objects.create(user=user.get(), code=code)
                    send_sms_code(phone, code)
                    return Response({'message': 'Token was created successfully'}, status=status.HTTP_201_CREATED)
                return Response({'message': 'This phone number doesn\'t exist'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'message': 'Incorrect phone number format'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetTokenView(GenericAPIView):
    """Endpoint that comes after forget password. Generates new token
    Args and Returns are the same as in /account/register/token
    """
    serializer_class = RegistrationForgetTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        phone = data['phone'].replace("+", "").replace("-", "").replace(" ", "")
        code = data['code']
        password1 = data['password1']
        password2 = data['password2']
        token = TokenModel.objects.filter(code=code, user__profile__phone=phone)
        if not token.exists():
            return Response({'message': 'Code is incorrect', 'status': False}, status=status.HTTP_200_OK)
        time_diff = (timezone.now() - token.get().created_at).total_seconds() / 60
        if time_diff > 5:
            return Response({'message': 'Code is expired'}, status=status.HTTP_400_BAD_REQUEST)
        if password1 != password2:
            return Response({'message': 'Passwords are not the same'}, status=status.HTTP_400_BAD_REQUEST)
        user = token.get().user
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        TokenModel.objects.filter(user=user).delete()
        user.set_password(password1)
        user.is_active = True
        user.save()
        data = {'token': token}
        expiration = (timezone.now() + api_settings.JWT_EXPIRATION_DELTA)
        response = Response(data, status=status.HTTP_200_OK)
        response.set_cookie(api_settings.JWT_AUTH_COOKIE, token, expires=expiration, httponly=True, secure=True)
        return response


class ProfileView(RetrieveUpdateAPIView):
    """Returns or updates profile
    Method GET for return
    Method PUT for update
    Args for PUT request:
        All args are optional but one of them should be compulsory
        profile: {"dob": "2003-02-02", "gender": "man"} // for gender send man/woman, dob in a form YYYY-mm-dd
        email
        last_name
        first_name Returns:
        {
            "id": 5,
            "username": "998999999999",
            "first_name": "rrr",
            "last_name": "rrr",
            "email": "mail202@gmail.com",
            "profile": {
                "dob": "2002-02-02",
                "gender": "woman"
            }
        }
    """
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        return super(ProfileView, self).get(request)


class UserDeleteView(DestroyAPIView):
    """User deletes himself account
    If successfully deleted returns: Successfully deleted
    """
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response("Successfully deleted", status=status.HTTP_204_NO_CONTENT)


class UserStatus(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        if ProfileModel.objects.filter(user=self.request.user).exists():
            data = {"username": self.request.user.username, "first_name": self.request.user.first_name,
                    "last_name": self.request.user.last_name, "phone": self.request.user.profile.phone,
                    "email": self.request.user.email, "permission": self.request.user.profile.get_permission_display(),
                    "used_trial": self.request.user.profile.used_trial,
                    "notifications": NotificationModel.objects.filter(seen=False, to_user=self.request.user).count()}
            if not self.request.user.profile.avatar:
                data["avatar"] = None
            else:
                data["avatar"] = request.build_absolute_uri(self.request.user.profile.avatar.url)
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response("User does not have profile", status=status.HTTP_400_BAD_REQUEST)


class UserListView(ListAPIView):
    permission_classes = [IsAuthenticated, HighPermission]
    serializer_class = UserDABSerializer

    def get_queryset(self):
        if self.request.user.profile.permission == 3:
            return UserModel.objects.all().order_by('first_name')
        elif self.request.user.profile.permission == 2:
            return UserModel.objects.filter(userboughtcoursemodel__in=UserBoughtCourseModel.objects.filter(
                course__mentor__user=self.request.user)).order_by('first_name')


class UserDetailView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, AdminPermission]
    serializer_class = UserDABSerializer
    queryset = UserModel.objects.all()
    lookup_url_kwarg = 'id'

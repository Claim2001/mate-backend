import datetime
import logging
import random
import string
from datetime import datetime
from urllib.parse import urlencode

import pycurl
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import jwt_response_payload_handler

from account.models import UserModel, ProfileModel

logger = logging.getLogger(__file__)


def send_sms_code(phone, code):
    sms = pycurl.Curl()
    sms.setopt(sms.URL, 'http://185.8.212.184/smsgateway/')
    adddata = '[{"phone": "%s", "text": "Ваш код для MATE LMS: %d. Sizning MATE LMS kodi: %d"}]' % (
        phone, code, code)
    payload = {'login': 'ITACADEMY', 'password': 'udYZ8fu5w8QwDA4592pe', 'data': adddata}
    payload = urlencode(payload)
    sms.setopt(sms.HEADER, 0)
    sms.setopt(sms.POST, 1)
    sms.setopt(sms.CONNECTTIMEOUT, 5)
    sms.setopt(sms.TIMEOUT, 5)
    sms.setopt(sms.SSL_VERIFYPEER, False)
    sms.setopt(sms.SSL_VERIFYHOST, 0)
    sms.setopt(sms.POSTFIELDS, payload)
    sms.setopt(sms.USERAGENT, 'Opera 10.00')
    sms.perform()
    sms.close()


def generate_token(length):
    return ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(length))


def generate_code():
    return random.randint(10000, 99999)


def send_code(phone, code):
    text = 'Mate'


class NewJSONWebTokenAPIView(APIView):
    """
    Base API View that various JWT interactions inherit from.
    """
    permission_classes = ()
    authentication_classes = ()

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'request': self.request,
            'view': self,
        }

    def get_serializer_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.serializer_class`.
        You may want to override this if you need to provide different
        serializations depending on the incoming request.
        (Eg. admins get full serialization, others get basic serialization)
        """
        assert self.serializer_class is not None, (
                "'%s' should either include a `serializer_class` attribute, "
                "or override the `get_serializer_class()` method."
                % self.__class__.__name__)
        return self.serializer_class

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            response_data = jwt_response_payload_handler(token, user, request)
            if UserModel.objects.filter(username=user.username).exists() and ProfileModel.objects.filter(
                    user=user).exists():
                um = UserModel.objects.get(username=user.username)
                response_data["username"] = um.username
                response_data["first_name"] = um.first_name
                response_data["last_name"] = um.last_name
                response_data["phone"] = um.profile.phone
                response_data["email"] = um.email
                response_data["permission"] = um.profile.get_permission_display()
                response_data["used_trial"] = um.profile.used_trial
                if not um.profile.avatar:
                    response_data["avatar"] = None
                else:
                    response_data["avatar"] = request.build_absolute_uri(UserModel.objects.get(username=user.username).profile.avatar.url)

            response = Response(response_data)
            if api_settings.JWT_AUTH_COOKIE:
                expiration = (datetime.utcnow() +
                              api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                    token,
                                    expires=expiration, secure=True,
                                    httponly=True)
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NewObtainJSONWebToken(NewJSONWebTokenAPIView):
    """
    API View that receives a POST with a user's username and password.

    Returns a JSON Web Token that can be used for authenticated requests.
    """
    serializer_class = JSONWebTokenSerializer

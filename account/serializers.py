import datetime
import re

from dateutil.relativedelta import relativedelta
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from account.models import UserModel, TokenModel, ProfileModel
from account.utils import send_sms_code, generate_code
from courses.models import TeacherModel, CourseModel, UserBoughtCourseModel
from courses.utils import admin_attach


class RegistrationSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    dob = serializers.DateField(input_formats=["%d/%m/%Y"], format=['%d/%m/%Y'])
    gender = serializers.CharField()
    password1 = serializers.CharField()
    password2 = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()

    class Meta:
        model = UserModel
        fields = ['username', 'first_name', 'last_name', 'dob', 'gender', 'password1', 'password2', 'email', 'phone']
        depth = 1


class RegistrationTokenSerializer(serializers.ModelSerializer):
    phone = serializers.CharField()
    code = serializers.CharField()

    class Meta:
        model = TokenModel
        fields = ['code', 'phone']


class RegistrationForgetTokenSerializer(serializers.ModelSerializer):
    phone = serializers.CharField()
    code = serializers.CharField()
    password1 = serializers.CharField()
    password2 = serializers.CharField()

    class Meta:
        model = TokenModel
        fields = ['code', 'phone', 'password1', 'password2']


class RegistrationCompleteSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', default=None)

    def create(self, validated_data):
        user = self.context['user']
        user.email = validated_data.pop('user').get('email')
        user.save()
        return UserModel.objects.create(user=user, **validated_data)

    class Meta:
        model = UserModel
        fields = ['avatar', 'fio', 'about', 'role', 'email']


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['username', 'email']


class PasswordForgetCodeSerializer(serializers.Serializer):
    phone = serializers.CharField()


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileModel
        fields = ['dob', 'gender', 'avatar', 'phone']


class ProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False)
    dob = serializers.DateField(required=False, input_formats=["%d/%m/%Y"], format=['%d/%m/%Y'])
    gender = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)
    old_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False)
    new_password2 = serializers.CharField(write_only=True, required=False)

    def to_representation(self, instance):
        a = super(ProfileSerializer, self).to_representation(instance)
        a['dob'] = datetime.datetime.strftime(instance.profile.dob, "%d/%m/%Y")
        a['gender'] = instance.profile.gender
        if instance.profile.phone:
            a['phone'] = instance.profile.phone.replace("+", "").replace("-", "").replace(" ", "")
        else:
            a['phone'] = None
        a["avatar"] = self.context['request'].build_absolute_uri(
            instance.profile.avatar.url) if instance.profile.avatar else None
        return a

    def update(self, instance, validated_data):
        profile = instance.profile
        if 'phone' in validated_data:
            phone = validated_data.pop('phone').replace("+", "").replace(" ", "").replace("-", "")
            if re.match(r'^998\d{9}$', phone):
                if ProfileModel.objects.filter(phone=phone).exists():
                    raise ParseError("This phone number is already used")
                profile.phone = phone
            else:
                raise ParseError("Wrong phone number format")
        if 'dob' in validated_data:
            profile.dob = validated_data.pop('dob')
        if 'gender' in validated_data:
            profile.gender = validated_data.pop('gender')
        if 'avatar' in validated_data:
            profile.avatar = validated_data.pop('avatar')
        if 'old_password' in validated_data:
            user = authenticate(self.context['request'], username=instance.username,
                                password=validated_data['old_password'])
            if user is None:
                raise ParseError("Wrong old password")
        if 'new_password' in validated_data and 'new_password2' in validated_data:
            if validated_data['new_password'] != validated_data['new_password2']:
                raise ParseError("New passwords are not the same")
        if 'old_password' in validated_data and 'new_password' in validated_data and 'new_password2' in validated_data:
            validated_data.pop('old_password')
            new_password = validated_data.pop('new_password')
            validated_data.pop('new_password2')
            instance.set_password(new_password)
        profile.save()
        return super(ProfileSerializer, self).update(instance, validated_data)

    class Meta:
        model = UserModel
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'dob', 'gender', 'avatar', 'phone',
                  'old_password', 'new_password', 'new_password2']
        read_only_fields = ['id']


class ProfileForUserSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        instance.permission = instance.get_permission_display()
        return super(ProfileForUserSerializer, self).to_representation(instance)

    class Meta:
        model = ProfileModel
        fields = '__all__'


class UBSerializer(serializers.ModelSerializer):
    course = serializers.CharField(source='course.title_lms')

    class Meta:
        model = UserBoughtCourseModel
        fields = ['course', 'expiration_date', 'trial']


class UserDABSerializer(serializers.ModelSerializer):
    permission = serializers.IntegerField(write_only=True)
    image = serializers.ImageField(write_only=True, required=False)
    description = serializers.CharField(write_only=True, required=False)
    bought_courses = serializers.SerializerMethodField()

    def get_bought_courses(self, obj):
        return UBSerializer(UserBoughtCourseModel.objects.filter(user=obj), many=True).data

    def to_representation(self, instance):
        a = super(UserDABSerializer, self).to_representation(instance)
        a["permission"] = instance.profile.get_permission_display()
        if instance.profile.avatar:
            a["avatar"] = self.context['request'].build_absolute_uri(instance.profile.avatar.url)
        else:
            a["avatar"] = None
        if TeacherModel.objects.filter(user=instance).exists():
            a['image'] = self.context['request'].build_absolute_uri(instance.teachermodel.image.url)
            a['description'] = instance.teachermodel.description
        a['full_name'] = f"{instance.first_name} {instance.last_name}"
        return a

    def update(self, instance, validated_data):
        if 'permission' in validated_data:
            permission = validated_data.pop('permission')
            user = self.context['request'].user
            if instance.profile.permission >= user.profile.permission and not user.is_superuser:
                raise ParseError(detail="User is the same level as you or higher")
            ProfileModel.objects.filter(user=instance).update(permission=permission)
            if permission == 1:
                if CourseModel.objects.filter(teacher__user=instance).exists():
                    raise ParseError("Put new teacher instead of this for courses")
                TeacherModel.objects.filter(user=instance).delete()
            elif permission == 2:
                try:
                    image = validated_data.pop('image')
                    description = validated_data.pop('description')
                except KeyError:
                    raise ParseError(detail="Send image and description")
                TeacherModel.objects.update_or_create(user=instance,
                                                      defaults={'image': image, 'description': description,
                                                                'full_name': f"{instance.first_name} {instance.last_name}"})
            elif permission == 3:
                for b in CourseModel.objects.filter(active=True):
                    if not UserBoughtCourseModel.objects.filter(user=instance, course=b).exists():
                        admin_attach(course=b, user=instance)
                    else:
                        UserBoughtCourseModel.objects.filter(user=instance, course=b).update(
                            expiration_date=timezone.now() + relativedelta(years=1000))
        return super(UserDABSerializer, self).update(instance, validated_data)

    class Meta:
        model = UserModel
        fields = ['id', 'username', 'is_active', 'permission', 'image', 'description', 'bought_courses']

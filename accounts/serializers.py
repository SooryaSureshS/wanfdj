from rest_framework import serializers
from accounts.models import User, UserLoginHistoryList, CharacterOwned, CharacterArmor, CharacterTool
from accounts.models import Form, Class
from django.utils.translation import gettext as _
from rest_framework.validators import UniqueValidator
from django.contrib.auth import authenticate
from role_settings.models import RoleSetting
import random


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'user_id', 'role_id')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        users = User.objects.create_user(validated_data['email'], validated_data['password'])
        return users


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    user_id = serializers.IntegerField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    english_name = serializers.CharField(min_length=2)
    chinese_name = serializers.CharField(min_length=2)
    password = serializers.CharField(min_length=8)

    def create(self, validated_data):
        extra_fields = {}
        email = None
        extra_fields['email'] = email
        if validated_data.get('email'):
            email = validated_data['email']
            extra_fields['email'] = email
        phone = None
        extra_fields['phone'] = phone
        if validated_data.get('phone'):
            phone = validated_data['phone']
            extra_fields['phone'] = phone
        english_name = None
        extra_fields['english_name'] = english_name
        if validated_data.get('english_name'):
            english_name = validated_data['english_name']
            extra_fields['english_name'] = english_name
        chinese_name = None
        extra_fields['chinese_name'] = chinese_name
        if validated_data.get('chinese_name'):
            chinese_name = validated_data['chinese_name']
            extra_fields['chinese_name'] = chinese_name
        is_superuser = False
        extra_fields['is_superuser'] = is_superuser
        if validated_data.get('is_superuser'):
            is_superuser = validated_data['is_superuser']
            extra_fields['is_superuser'] = is_superuser
            if is_superuser:
                extra_fields['is_staff'] = True
                extra_fields['is_superuser'] = True
        users = User.objects.create_user(validated_data['email'], validated_data['password'],
                                         validated_data['english_name'], validated_data['chinese_name'],
                                         extra_fields)
        return users

    class Meta:
        model = User
        fields = (
            'id', 'user_id', 'english_name', 'email', 'password', 'phone', 'chinese_name', 'gender', 'login_points')


class AdminRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    user_id = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(min_length=8)

    class Meta:
        model = User
        fields = ("user_id", "email", "password", "role_id", 'remarks')

    def save(self):
        user = super(AdminRegisterSerializer, self).save()
        role_setting = RoleSetting.objects.filter(id=self['role_id'].value).first()
        user.email = self['email'].value
        user.user_id = self['email'].value
        user.password_string = self['password'].value
        user.set_password(self['password'].value)
        user.role_id = role_setting
        user.is_admin = True
        user.is_staff = True
        user.remarks = self['remarks'].value
        user.save()
        return user


class StudentCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    user_id = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    student_id = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(min_length=8)
    chinese_name = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    english_name = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ("english_name", 'chinese_name', 'class_no', 'class_id', 'form_id',
                  'gender', 'birth_date', 'student_id', 'password', 'user_status',
                  'personal_profile', 'user_id', 'email')

    def save(self):
        user = super(StudentCreateSerializer, self).save()
        user.english_name = self['english_name'].value
        user.chinese_name = self['chinese_name'].value
        user.class_no = self['class_no'].value
        user.gender = self['gender'].value
        user.birth_date = self['birth_date'].value
        user.student_id = self['student_id'].value
        user.email = self['email'].value
        user.user_id = self['email'].value
        user.set_password(str(random.randint(0, 9)))
        user.user_status = self['user_status'].value
        user.is_admin = False
        user.is_staff = False
        user.is_student = True
        user.personal_profile = self['personal_profile'].value
        user.save()
        return user


class TokenSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = (
            'id', 'user_id', 'english_name', 'chinese_name', 'email', 'password', 'gender' 'phone', 'login_points',
            'personal_profile')


class LoginHistorySerializers(serializers.ModelSerializer):
    class Meta:
        model = UserLoginHistoryList
        fields = ('id', 'user_id', 'created_date', 'created_date_time', 'updated_date')


class StudentLoginSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = '__all__'

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_student:
            if user and user.is_active:
                return user
        raise serializers.ValidationError({
            'warning': _('Incorrect Credentials Passed.')
        })


class AdminLoginSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = '__all__'

    def validate(self, data):
        user = authenticate(**data)
        if user and not user.is_student:
            if user and user.is_active:
                return user
        raise serializers.ValidationError({
            'warning': _('Incorrect Credentials Passed.')
        })


class UserEditSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'


class CharacterOwnedSerializer(serializers.ModelSerializer):

    class Meta:
        model = CharacterOwned
        fields = '__all__'


class CharacterArmorSerializer(serializers.ModelSerializer):

    class Meta:
        model = CharacterArmor
        fields = '__all__'


class CharacterToolSerializer(serializers.ModelSerializer):

    class Meta:
        model = CharacterTool
        fields = '__all__'


class FormSerializer(serializers.ModelSerializer):

    class Meta:
        model = Form
        fields = (
            'id', 'form_name', 'active', 'created_date',
            'updated_date')


class ClassSerializer(serializers.ModelSerializer):

    class Meta:
        model = Class
        fields = '__all__'

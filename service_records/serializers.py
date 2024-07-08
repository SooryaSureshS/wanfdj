from rest_framework import serializers
from .models import ServiceRecords, ServiceRecordNotAppreciatedUsers
from accounts.models import User
from rest_framework.validators import UniqueValidator
import random


class ServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRecords
        fields = '__all__'


class ServiceRecordNotAppreciatedUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRecordNotAppreciatedUsers
        fields = '__all__'


class AddStudentCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    user_id = serializers.CharField(
        required=False)
    student_id = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(required=False, min_length=8)
    chinese_name = serializers.CharField(
        required=True)
    english_name = serializers.CharField(
        required=True)
    birth_date = serializers.DateField(required=False)

    class Meta:
        model = User
        fields = ("english_name", 'chinese_name', 'class_no', 'class_id', 'form_id',
                  'gender', 'birth_date', 'student_id', 'password', 'user_status',
                  'personal_profile', 'user_id', 'email', 'is_student')


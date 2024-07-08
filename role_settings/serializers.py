from rest_framework import serializers
from .models import RoleSetting


class RoleSettingSerializer(serializers.ModelSerializer):

    class Meta:
        model = RoleSetting
        fields = '__all__'

from rest_framework import serializers
from .models import RecoverVitality


class RecoverVitalitySerializer(serializers.ModelSerializer):

    class Meta:
        model = RecoverVitality
        fields = '__all__'

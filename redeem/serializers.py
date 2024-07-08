from rest_framework import serializers
from .models import Redeem, RedeemRecord


class RedeemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Redeem
        fields = '__all__'


class RedeemRecordsSerializer(serializers.ModelSerializer):

    class Meta:
        model = RedeemRecord
        fields = '__all__'

from rest_framework import serializers
from service_records.models import ServiceRecords
from accounts.models import Class


class ServicesSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServiceRecords
        fields = '__all__'


class ClassesSerializers(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = '__all__'



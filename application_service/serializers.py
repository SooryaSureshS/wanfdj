from rest_framework import serializers
from .models import ApplicationService, TeachersSharing, ApplicationServiceApplicants, Notification


class ApplicationServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = ApplicationService
        fields = '__all__'


class ApplicationServiceApplicantsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ApplicationServiceApplicants
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = '__all__'


class TeachersSharingSerializer(serializers.ModelSerializer):

    class Meta:
        model = TeachersSharing
        fields = '__all__'

from django.db import models
from django.contrib import admin
from accounts.models import User, Form, Class
from django.utils.translation import gettext as _


class ApplicationService(models.Model):
    teacher_name = models.CharField(max_length=250, blank=True, null=True)
    no_of_students = models.IntegerField(blank=False, null=True)
    SERVICE_CHOICES = (
        ('community', 'Community Services'),
        ('school', 'School Services'),
    )
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES, blank=True, null=True)

    service_date = models.DateField(editable=True, blank=True, null=True)
    serving_from_time = models.TimeField(editable=True, blank=True, null=True)
    serving_to_time = models.TimeField(editable=True, blank=True, null=True)

    service_description = models.TextField(blank=True, null=True)
    publish_date = models.DateField(editable=True, blank=True, null=True)
    publish_time = models.TimeField(editable=True, blank=True, null=True)

    location = models.CharField(max_length=250, blank=True, null=True)
    attachment = models.FileField(_("attachment"), upload_to='media/', blank=True, null=True)
    status = models.BooleanField(default=False)

    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)
    service_deadline_date = models.DateField(editable=True, blank=True, null=True)
    service_deadline_time = models.TimeField(editable=True, blank=True, null=True)

    @property
    def full_name(self):
        return '%s' % self.teacher_name

    @property
    def show_name(self):
        return '%s' % self.teacher_name

    def __str__(self):
        return str(self.teacher_name)

    class Meta:
        ordering = ['id']


class ApplicationServiceList(admin.ModelAdmin):
    list_display = ('id', 'teacher_name', 'no_of_students', 'service_type',
                    'service_date', 'serving_from_time',
                    'serving_to_time', 'status', 'created_date')


class ApplicationServiceApplicants(models.Model):
    application_service_id = models.ForeignKey(ApplicationService, on_delete=models.CASCADE, null=True, blank=True)
    student_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    student_name = models.CharField(max_length=250, blank=True, null=True)
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, null=True, blank=True)
    class_no = models.CharField(max_length=255, blank=True, null=True)

    student_contact_no = models.CharField(max_length=17, blank=True, null=True, )
    parent_contact_no = models.CharField(max_length=17, blank=True, null=True, )
    parent_consent = models.BooleanField(default=False)
    date_of_application = models.DateField(auto_now_add=True, editable=False)
    STATUS = (
        ('waiting', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('disapproved', 'Disapproved'),
    )
    status = models.CharField(max_length=20, default='waiting', choices=STATUS, blank=True, null=True)

    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)

    notification_opened_status = models.BooleanField(default=False)
    disapproval_date = models.DateTimeField(editable=False, blank=True, null=True)
    approval_date = models.DateTimeField(editable=False, blank=True, null=True)

    @property
    def full_name(self):
        return '%s' % self.student_name

    @property
    def show_name(self):
        return '%s' % self.student_name

    def __str__(self):
        return str(self.student_name)

    class Meta:
        ordering = ['id']


class ApplicationServiceApplicantsList(admin.ModelAdmin):
    list_display = ('id', 'student_id', 'student_name',
                    'class_no', 'class_id', 'application_service_id',
                    'parent_consent', 'date_of_application',
                    'status', 'created_date')


class Notification(models.Model):
    student_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    service_id = models.ForeignKey(ApplicationService, on_delete=models.CASCADE, null=True, blank=True)
    applicant_service_id = models.ForeignKey(ApplicationServiceApplicants, on_delete=models.CASCADE, null=True,
                                             blank=True)
    reminder = models.TextField(blank=True, null=True)
    notification_opened_status = models.BooleanField(default=False)
    disapproval_date = models.DateTimeField(editable=False, blank=True, null=True)
    approval_date = models.DateTimeField(editable=False, blank=True, null=True)
    approval_status = models.CharField(max_length=20, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)


class NotificationList(admin.ModelAdmin):
    list_display = ('id', 'student_id', 'service_id', 'applicant_service_id', 'reminder',
                    'notification_opened_status', 'disapproval_date',
                    'approval_date', 'approval_status')


admin.site.register(Notification, NotificationList)


class TeachersSharing(models.Model):
    teacher_name = models.CharField(max_length=250, blank=True, null=True)
    service_date = models.DateField(editable=True, blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    attachment = models.FileField(_("attachment"), upload_to='media/', blank=True, null=True)
    status = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)

    @property
    def full_name(self):
        return '%s' % self.teacher_name

    @property
    def show_name(self):
        return '%s' % self.teacher_name

    def __str__(self):
        return str(self.teacher_name)

    class Meta:
        ordering = ['id']


class TeachersSharingList(admin.ModelAdmin):
    list_display = ('id', 'teacher_name', 'service_date', 'title',
                    'status', 'created_date')


admin.site.register(ApplicationService, ApplicationServiceList)
admin.site.register(ApplicationServiceApplicants, ApplicationServiceApplicantsList)
admin.site.register(TeachersSharing, TeachersSharingList)

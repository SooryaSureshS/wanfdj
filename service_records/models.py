from django.db import models
from django.contrib import admin
from accounts.models import User
from django.utils.translation import gettext as _


class ServiceRecords(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE,
                                null=True, blank=True)
    is_community_service = models.BooleanField(default=False)
    is_school_service = models.BooleanField(default=False)
    is_home_service = models.BooleanField(default=False)

    SERVICE_CHOICES = (
        ('community', 'Community Services'),
        ('school', 'School Services'),
        ('home', 'Home Services'),
    )

    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES, blank=True, null=True)
    category = models.CharField(max_length=250, blank=True, null=True)
    reflection = models.TextField(blank=True, null=True)
    serving_date = models.DateField(editable=True, blank=True, null=True)
    serving_from_time = models.TimeField(editable=True, blank=True, null=True)
    serving_to_time = models.TimeField(editable=True, blank=True, null=True)
    serving_from_date_time = models.DateTimeField(editable=True, blank=True, null=True)
    serving_to_date_time = models.DateTimeField(editable=True, blank=True, null=True)
    service_duration = models.CharField(max_length=100, blank=True, null=True)
    photo = models.ImageField(_("Image"), upload_to='media/', blank=True, null=True)
    APPROVAL_CHOICES = (
        ('waiting', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('disapproved', 'Disapproved'),
    )
    approval_status = models.CharField(max_length=20, choices=APPROVAL_CHOICES, blank=True, null=True,
                                       default='waiting')
    is_shared = models.BooleanField(default=False)
    appreciated_user_1 = models.ForeignKey(User, related_name='appreciated_user_1',
                                           db_column='appreciated_user_1',
                                           on_delete=models.CASCADE, null=True, blank=True)
    appreciated_user_2 = models.ForeignKey(User, related_name='appreciated_user_2',
                                           db_column='appreciated_user_2',
                                           on_delete=models.CASCADE, null=True, blank=True)
    appreciated_user_3 = models.ForeignKey(User, related_name='appreciated_user_3',
                                           db_column='appreciated_user_3',
                                           on_delete=models.CASCADE, null=True, blank=True)
    disapproval_reason = models.TextField(blank=True, null=True)
    program_nature = models.TextField(blank=True, null=True)
    service_organization = models.CharField(max_length=250, blank=True, null=True)
    person_in_charge_name = models.CharField(max_length=250, blank=True, null=True)
    person_in_charge_contact_no = models.CharField(max_length=250, blank=True, null=True)
    teacher_in_charge_name = models.CharField(max_length=250, blank=True, null=True)
    teacher_in_charge_contact_no = models.CharField(max_length=250, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)
    teacher_approved = models.BooleanField(default=False)

    disapproval_status = models.BooleanField(default=False)
    counter = models.IntegerField(default=0)
    notification_opened_status = models.BooleanField(default=False)
    disapproval_date = models.DateTimeField(editable=False, blank=True, null=True)

    @property
    def full_name(self):
        return '%s' % self.user_id

    @property
    def show_name(self):
        return '%s' % self.category

    def __str__(self):
        return str(self.category)

    class Meta:
        ordering = ['id']


class ServiceRecordsList(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'service_type', 'approval_status',
                    'category', 'serving_date', 'serving_from_time',
                    'serving_to_time', 'is_shared', 'is_active', 'created_date')


class ServiceRecordAppreciatedUsers(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE,
                                null=True, blank=True)
    service_record_id = models.ForeignKey(ServiceRecords, on_delete=models.CASCADE,
                                          null=True, blank=True)
    created_date_val = models.DateField(editable=True, null=True, blank=True, )
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)


class ServiceRecordAppreciatedUsersList(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'service_record_id', 'created_date_val', 'created_date')


class ServiceRecordNotAppreciatedUsers(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE,
                                null=True, blank=True)
    service_record_id = models.ForeignKey(ServiceRecords, on_delete=models.CASCADE,
                                          null=True, blank=True)
    created_date_val = models.DateField(editable=True, null=True, blank=True, )
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)


class ServiceRecordNotAppreciatedUsersList(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'service_record_id', 'created_date_val', 'created_date')


admin.site.register(ServiceRecords, ServiceRecordsList)
admin.site.register(ServiceRecordAppreciatedUsers, ServiceRecordAppreciatedUsersList)
admin.site.register(ServiceRecordNotAppreciatedUsers, ServiceRecordNotAppreciatedUsersList)

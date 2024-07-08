from django.db import models
from django.contrib import admin
from django.utils.translation import gettext as _


class RoleSetting(models.Model):

    role_title = models.CharField(null=True, blank=True, max_length=255)
    LEVEL_CHOICES = (
        ('level_1', 'Level 1'),
        ('level_2', 'Level 2'),
        ('level_3', 'Level 3'),
        ('customise', 'customise'),
    )
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, blank=True, null=True,
                             default='level_1')
    all_privileges = models.BooleanField(default=False)

    records_approval = models.BooleanField(default=False)
    records_approval_home = models.BooleanField(default=False)
    records_approval_school = models.BooleanField(default=False)
    records_approval_community = models.BooleanField(default=False)

    post_services = models.BooleanField(default=False)
    post_services_teachers_sharing = models.BooleanField(default=False)
    post_services_school = models.BooleanField(default=False)
    post_services_community = models.BooleanField(default=False)

    monitoring = models.BooleanField(default=False)
    monitoring_chat_room = models.BooleanField(default=False)
    monitoring_home_service = models.BooleanField(default=False)
    monitoring_share_record_area = models.BooleanField(default=False)

    service_record = models.BooleanField(default=False)
    service_record_import = models.BooleanField(default=False)
    service_record_export_full_list = models.BooleanField(default=False)
    service_record_export_individual_record = models.BooleanField(default=False)
    service_record_add_student = models.BooleanField(default=False)

    redeemed_items = models.BooleanField(default=False)
    redeem_item_list = models.BooleanField(default=False)
    redeem_item_record = models.BooleanField(default=False)

    role_setting = models.BooleanField(default=False)
    add_role = models.BooleanField(default=False)
    edit_role = models.BooleanField(default=False)
    delete_role = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)

    @property
    def full_name(self):
        return '%s' % self.role_title

    @property
    def show_name(self):
        return '%s' % self.role_title

    def __str__(self):
        return str(self.role_title)

    class Meta:
        ordering = ['id']


class RoleSettingList(admin.ModelAdmin):
    list_display = ('id', 'role_title', 'level', 'all_privileges', 'records_approval',
                    'post_services', 'monitoring', 'service_record', 'redeemed_items',
                    'role_setting', 'is_active', 'created_date')


admin.site.register(RoleSetting, RoleSettingList)

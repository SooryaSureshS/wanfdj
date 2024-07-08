from django.db import models
from django.contrib import admin
from accounts.models import User, Form, Class
from django.utils.translation import gettext as _


class Redeem(models.Model):
    item_name = models.CharField(max_length=250, blank=True, null=True)
    rubies = models.IntegerField(blank=False, null=True)
    value = models.FloatField(blank=False, null=True)
    amount = models.FloatField(blank=False, null=True)
    teachers_name = models.CharField(max_length=250, blank=True, null=True)
    icon = models.FileField(_("Icon"), upload_to='media/', blank=True, null=True)
    status = models.BooleanField(default=False)
    REDEEM_CHOICES = (
        ('regular', 'Regular'),
        ('special', 'Special'),
    )
    redeem_type = models.CharField(max_length=10, choices=REDEEM_CHOICES, blank=True, null=True, default='special')
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)

    introduction = models.CharField(max_length=250, blank=True, null=True)
    stock = models.IntegerField(blank=True, null=True)

    @property
    def full_name(self):
        return '%s' % self.item_name

    @property
    def show_name(self):
        return '%s' % self.item_name

    def __str__(self):
        return str(self.item_name)

    class Meta:
        ordering = ['id']


class RedeemList(admin.ModelAdmin):
    list_display = ('id', 'item_name', 'redeem_type', 'rubies', 'value',
                    'amount', 'teachers_name', 'status', 'created_date')


class RedeemRecord(models.Model):
    request_date = models.DateField(auto_now_add=True, editable=True, blank=True, null=True)
    item_id = models.ForeignKey(Redeem, on_delete=models.CASCADE,
                                null=True, blank=True)
    value = models.FloatField(blank=False, null=True)
    STATUS = (
        ('waiting', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('disapproved', 'Disapproved'),
    )
    status = models.CharField(max_length=20, default='waiting', choices=STATUS, blank=True, null=True)
    teachers_name = models.CharField(max_length=250, blank=True, null=True)
    student_id = models.ForeignKey(User, on_delete=models.CASCADE,
                                   null=True, blank=True)
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, null=True, blank=True)
    class_no = models.CharField(max_length=250, blank=True, null=True)
    receive_date = models.DateField(auto_now_add=True, editable=True, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    REDEEM_CHOICES = (
        ('regular', 'Regular'),
        ('special', 'Special'),
    )
    redeem_type = models.CharField(max_length=10, choices=REDEEM_CHOICES, blank=True, null=True)

    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)

    @property
    def full_name(self):
        return '%s' % self.item_id

    @property
    def show_name(self):
        return '%s' % self.item_id

    def __str__(self):
        return str(self.item_id)

    class Meta:
        ordering = ['id']


class RedeemRecordsList(admin.ModelAdmin):
    list_display = ('id', 'item_id', 'value', 'teachers_name', 'student_id', 'status', 'created_date')


admin.site.register(Redeem, RedeemList)
admin.site.register(RedeemRecord, RedeemRecordsList)

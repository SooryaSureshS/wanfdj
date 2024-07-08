from django.db import models
from django.contrib import admin
# from accounts.models import User
from django.utils.translation import gettext as _


class RecoverVitality(models.Model):
    wamfo_coins = models.IntegerField(_("Wamfo Coins"), blank=True, null=True, default=0)
    vitality = models.IntegerField(_("Vitality"), blank=True, null=True, default=0)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)

    @property
    def full_name(self):
        return '%s' % self.wamfo_coins

    @property
    def show_name(self):
        return '%s' % self.wamfo_coins

    def __str__(self):
        return str(self.wamfo_coins)

    class Meta:
        ordering = ['id']


class RecoverVitalityList(admin.ModelAdmin):
    list_display = ('id', 'wamfo_coins', 'vitality',
                    'created_date')


admin.site.register(RecoverVitality, RecoverVitalityList)

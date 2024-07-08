from django.db import models
from django.contrib import admin
# from accounts.models import User
from django.utils.translation import gettext as _


class Character(models.Model):
    name = models.CharField(max_length=250, blank=True, null=True)
    CHARACTER_CHOICES = (
        ('normal', 'Normal'),
        ('rare', 'Rare'),
        ('super_rare', 'Super Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary'),
    )
    character_type = models.CharField(max_length=55, choices=CHARACTER_CHOICES, blank=True, null=True)
    character_image = models.ImageField(_("Image"), upload_to='media/', blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)


    @property
    def full_name(self):
        return '%s' % self.name

    @property
    def show_name(self):
        return '%s' % self.name

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['id']


class CharacterList(admin.ModelAdmin):
    list_display = ('id', 'name', 'character_type',
                    'created_date')


class Armor(models.Model):
    name = models.CharField(max_length=250, blank=True, null=True)
    armor_image = models.ImageField(_("Image"), upload_to='media/', blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)

    @property
    def full_name(self):
        return '%s' % self.name

    @property
    def show_name(self):
        return '%s' % self.name

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['id']


class ArmorList(admin.ModelAdmin):
    list_display = ('id', 'name',
                    'created_date')


class Tool(models.Model):
    name = models.CharField(max_length=250, blank=True, null=True)
    tool_image = models.ImageField(_("Image"), upload_to='media/', blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)

    @property
    def full_name(self):
        return '%s' % self.name

    @property
    def show_name(self):
        return '%s' % self.name

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['id']


class ToolList(admin.ModelAdmin):
    list_display = ('id', 'name',
                    'created_date')


admin.site.register(Character, CharacterList)
admin.site.register(Tool, ToolList)
admin.site.register(Armor, ArmorList)

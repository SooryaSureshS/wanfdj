from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .manager import CustomUserManager
from django.contrib import admin
from role_settings.models import RoleSetting
from django.utils.translation import gettext as _
from character.models import Character, Armor, Tool


class Form(models.Model):
    form_name = models.CharField(max_length=200, null=True, blank=True)
    active = models.BooleanField(default=True)
    created_date = models.DateField(auto_now_add=True, editable=True, null=True, blank=True, )
    created_date_time = models.DateTimeField(auto_now_add=True, editable=True, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now_add=True, editable=True, null=True, blank=True)

    def __str__(self):
        return str(self.form_name)

    class Meta:
        ordering = ['form_name']


class FormList(admin.ModelAdmin):
    list_display = ('id', 'form_name', 'active',
                    'created_date', 'created_date_time', 'updated_date')


class Class(models.Model):

    form_id = models.ForeignKey(Form, on_delete=models.CASCADE, null=True, blank=True)
    class_name = models.CharField(max_length=200, default='', null=True, blank=True)
    active = models.BooleanField(default=True)
    created_date = models.DateField(auto_now_add=True, editable=True, null=True, blank=True, )
    created_date_time = models.DateTimeField(auto_now_add=True, editable=True, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now_add=True, editable=True, null=True, blank=True)

    def __str__(self):
        return str(self.class_name)

    class Meta:
        ordering = ['class_name']


class ClassList(admin.ModelAdmin):
    list_display = ('id', 'form_id', 'class_name', 'active',
                    'created_date', 'created_date_time', 'updated_date')


class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(unique=True, blank=False, null=False, max_length=255,
                               error_messages={'unique': "This Username has already been registered."})
    student_id = models.CharField(blank=True, null=True, max_length=255)
    role_id = models.ForeignKey(RoleSetting, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(unique=True, max_length=255, blank=True, null=True,
                              error_messages={'unique': "This email has already been registered."})
    sequence = models.CharField(max_length=10, blank=True, null=True)
    phone = models.CharField(max_length=17, blank=True, null=True, )
    student_phone_no = models.CharField(max_length=17, blank=True, null=True, )
    parent_phone_no = models.CharField(max_length=17, blank=True, null=True, )

    form_id = models.ForeignKey(Form, on_delete=models.CASCADE, null=True, blank=True)
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, null=True, blank=True)

    class_no = models.CharField(max_length=255, blank=True, null=True)
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Others'),
    )
    gender = models.CharField(max_length=5, choices=GENDER_CHOICES, blank=True, null=True)
    birth_date = models.DateField(editable=True, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='media/', blank=True, null=True, )
    home_service_duration = models.IntegerField(blank=True, null=True, default=0)
    school_service_duration = models.IntegerField(blank=True, null=True, default=0)
    community_service_duration = models.IntegerField(blank=True, null=True, default=0)
    english_name = models.CharField(max_length=200, default='', null=True, blank=True)
    chinese_name = models.CharField(max_length=200, default='', null=True, blank=True)
    personal_profile = models.TextField(blank=True, null=True)
    registration_date = models.DateField(auto_now_add=True, editable=False, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)
    user_status = models.BooleanField(default=True, null=True, blank=True)
    is_new = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    otp = models.CharField(max_length=200, default=False, null=True, blank=True)
    password_string = models.CharField(max_length=255, null=True, blank=True)
    password_url = models.CharField(max_length=500, default="1234587469502jhjghfgfsfdsxfxs", null=True, blank=True)
    password_set_url = models.CharField(max_length=500, default="1", null=True, blank=True)

    # Game
    login_points = models.IntegerField(_("Wamfo Coins"), blank=True, null=True, default=0)
    student_rubies = models.IntegerField(_("Wamfo Rubies"), blank=True, null=True, default=0)
    student_vitality = models.IntegerField(_("Vitality"), blank=True, null=True, default=0)
    student_exp = models.IntegerField(_("EXP"), blank=True, null=True, default=0)

    remarks = models.CharField(max_length=500, default="1", null=True, blank=True)
    year_of_joining = models.CharField(max_length=10, null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'user_id'

    @property
    def full_name(self):
        return '%s %s' % (self.user_id, self.english_name)

    @property
    def show_name(self):
        return '%s' % self.english_name

    def __str__(self):
        return str(self.user_id)

    class Meta:
        ordering = ['-created_date']


class CharacterOwned(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    character_id = models.ForeignKey(Character, on_delete=models.CASCADE, null=True, blank=True)
    character_name = models.CharField(max_length=200, default='', null=True, blank=True)
    character_level = models.IntegerField(blank=True, null=True, default=1)
    character_hp = models.IntegerField(blank=True, null=True, default=1)
    dodge = models.IntegerField(blank=True, null=True, default=1)
    critical = models.IntegerField(blank=True, null=True, default=1)
    active = models.BooleanField(default=False)
    created_date = models.DateField(auto_now_add=True, editable=True, null=True, blank=True, )
    created_date_time = models.DateTimeField(auto_now_add=True, editable=True, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now_add=True, editable=True, null=True, blank=True)


class CharacterOwnedList(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'character_id', 'character_name', 'active',
                    'created_date', 'created_date_time', 'updated_date')


class CharacterArmor(models.Model):
    armor_id = models.ForeignKey(Armor, on_delete=models.CASCADE, null=True, blank=True)
    owned_character_id = models.ForeignKey(CharacterOwned, on_delete=models.CASCADE, null=True, blank=True)
    active = models.BooleanField(default=False)
    created_date = models.DateField(auto_now_add=True, editable=True, null=True, blank=True, )
    created_date_time = models.DateTimeField(auto_now_add=True, editable=True, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now_add=True, editable=True, null=True, blank=True)


class CharacterArmorsList(admin.ModelAdmin):
    list_display = ('id', 'armor_id', 'active',
                    'created_date', 'updated_date')


class CharacterTool(models.Model):
    tool_id = models.ForeignKey(Tool, on_delete=models.CASCADE, null=True, blank=True)
    owned_character_id = models.ForeignKey(CharacterOwned, on_delete=models.CASCADE, null=True, blank=True)
    active = models.BooleanField(default=False)
    created_date = models.DateField(auto_now_add=True, editable=True, null=True, blank=True, )
    created_date_time = models.DateTimeField(auto_now_add=True, editable=True, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now_add=True, editable=True, null=True, blank=True)


class CharacterToolsList(admin.ModelAdmin):
    list_display = ('id', 'tool_id', 'active',
                    'created_date', 'updated_date')


class UserLoginHistory(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_date = models.DateField(auto_now_add=True, editable=True, null=True, blank=True, )
    created_date_time = models.DateTimeField(auto_now_add=True, editable=True, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now_add=True, editable=True, null=True, blank=True)


class UserLoginHistoryList(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'created_date', 'created_date_time', 'updated_date')


admin.site.register(Form, FormList)
admin.site.register(Class, ClassList)
admin.site.register(User)
admin.site.register(UserLoginHistory, UserLoginHistoryList)
admin.site.register(CharacterOwned, CharacterOwnedList)
admin.site.register(CharacterArmor, CharacterArmorsList)
admin.site.register(CharacterTool, CharacterToolsList)

# noinspection GrazieInspection
""" WAMFO URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls.static import static
from knox import views as knox_views
from django.conf import settings
from accounts.admin_views import AdminSignInAPI, RoleSettingView, AdminPasswordReset
from accounts.admin_views import AdminResetTokenPasswordVerification, AdminPasswordVerification
from accounts.admin_views import TeacherList, StudentList, UserCreateAPI, UserListAPI, UserFormAPI
from accounts.admin_views import UserEditAPI, UserDeleteAPI
from accounts.student_views import StudentSignInAPI, StudentFirstTimeRegister, StudentHome
from accounts.student_views import StudentProfileView, StudentProfileEdit, RandomCharacterSelection
from accounts.student_views import StudentFirstTimeLoginVerification, StudentAccountTokenPasswordVerification
from accounts.admin_views import FormList, ClassList, ListAllUsersAPI

urlpatterns = [
    # Admin
    path('create', UserCreateAPI.as_view(), name='User'),
    path('list', UserListAPI.as_view(), name='User List'),
    path('form', UserFormAPI.as_view(), name='User Form'),
    path('edit', UserEditAPI.as_view(), name='User Edit'),
    path('delete', UserDeleteAPI.as_view(), name='User Delete'),
    path('list/users', ListAllUsersAPI.as_view(), name='User Delete'),
    path('admin/login/', AdminSignInAPI.as_view(), name='Admin Login'),
    path('role/setting', RoleSettingView.as_view(), name='Admin Login'),
    path('admin/password/reset', AdminPasswordReset.as_view(), name='Admin Password Reset'),
    path('admin/token/<str:token>', AdminResetTokenPasswordVerification.snippet_detail),
    path('admin/password/reset/<str:token>', AdminPasswordVerification.snippet_detail),

    # Student
    path('student/login/', StudentSignInAPI.as_view(), name='Student Login'),
    path('student/first/login/', StudentFirstTimeRegister.as_view(), name='Student First Time Login'),
    path('student/first/login/token/<str:token>', StudentAccountTokenPasswordVerification.snippet_detail),
    path('student/first/login/reset/<str:token>', StudentFirstTimeLoginVerification.snippet_detail),
    path('student/home', StudentHome.as_view(), name='Home Page'),
    path('student/view/profile', StudentProfileView.as_view(), name='View Profile'),
    path('student/edit/profile', StudentProfileEdit.as_view(), name='Home Page'),
    path('random/character/selection', RandomCharacterSelection.as_view(), name='Random Character Selection'),

    # All
    path('logout/', knox_views.LogoutView.as_view(), name='Logout'),
    path('logout/all/', knox_views.LogoutAllView.as_view(), name='Logout All'),
    path('teachers/', TeacherList.as_view(), name='Teacher List'),
    path('students/', StudentList.as_view(), name='Student List'),
    path('forms/', FormList.as_view(), name='Forms List'),
    path('classes/', ClassList.as_view(), name='Class List'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

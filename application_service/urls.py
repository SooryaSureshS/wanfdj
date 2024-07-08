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
from django.conf import settings
from application_service.views import ApplicationServices, ApplicationServicesFilter, ApplicationServicesNotification
from application_service.views import ApplicationServicesForm, TeachersSharingAPI, TeachersSharingForm
from application_service.views import TeachersSharingList, ApplicantUpdate, ActiveTeachersSharingList
from application_service.views import MissionAreaList, MissionAreaForm, MissionAreaAccept
from application_service.views import MyMissionList, MyMissionForm, MissionForm, MissionAreaAcceptUpdate

urlpatterns = [
    # Admin
    path('', ApplicationServices.as_view(), name='Application Services'),
    path('filter', ApplicationServicesFilter.as_view(), name='Application Services Filter'),
    path('form', ApplicationServicesForm.as_view(), name='Application Services Filter'),
    path('update/applicant', ApplicantUpdate.as_view(), name='Application Services Filter'),
    path('teachers/sharing', TeachersSharingAPI.as_view(), name='Teacher Sharing'),
    path('teachers/sharing/list', TeachersSharingList.as_view(), name='Teacher Sharing List'),
    path('teachers/sharing/form', TeachersSharingForm.as_view(), name='Teacher Sharing Form'),
    path('notification', ApplicationServicesNotification.as_view(), name='Application Services Notification'),

    # Student
    path('mission/area/list', MissionAreaList.as_view(), name='Mission Area List'),
    path('mission/area/form', MissionAreaForm.as_view(), name='Mission Area Form'),
    path('mission/area/accept', MissionAreaAccept.as_view(), name='Teacher Sharing Form'),
    path('mission/area/accept/update', MissionAreaAcceptUpdate.as_view(), name='Teacher Sharing Form'),
    path('my/mission/list', MyMissionList.as_view(), name='My Mission List'),
    path('my/mission/form', MyMissionForm.as_view(), name='My Mission Form'),
    path('teachers/sharing/list/active', ActiveTeachersSharingList.as_view(), name='Teacher Sharing List'),
    path('mission/form', MissionForm.as_view(), name='Mission Approval List')

    # All
]

urlpatterns = format_suffix_patterns(urlpatterns)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

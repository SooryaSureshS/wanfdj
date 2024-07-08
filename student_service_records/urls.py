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
from student_service_records.views import StudentRecordsFilter, AddStudents, StudentForm, StudentUpdate
from student_service_records.views import StudentServiceHome, StudentServiceCommunity, StudentServiceSchool
from student_service_records.views import StudentServiceHomeItem, StudentServiceCommunityItem, StudentServiceSchoolItem
from student_service_records.views import FormClassesFilter, StudentRecordsList

urlpatterns = [
    # Admin
    path('student/records/filter', StudentRecordsFilter.as_view(), name='Student Records'),
    path('student/records/list', StudentRecordsList.as_view(), name='Student Records'),
    path('add/student', AddStudents.as_view(), name='Add Students'),
    path('student/form', StudentForm.as_view(), name='Students Form'),
    path('student/update', StudentUpdate.as_view(), name='Update Students'),
    path('student/home/service', StudentServiceHome.as_view(), name='Home Service Students'),
    path('student/community/service', StudentServiceCommunity.as_view(), name='Community Service Students'),
    path('student/school/service', StudentServiceSchool.as_view(), name='School Service Students'),
    path('student/home/service/item', StudentServiceHomeItem.as_view(), name='Home Service Students'),
    path('student/community/service/item', StudentServiceCommunityItem.as_view(), name='Community Service Students'),
    path('student/school/service/item', StudentServiceSchoolItem.as_view(), name='School Service Students'),
    path('form/classes/filter', FormClassesFilter.as_view(), name='Form Classes Filter'),

    # Student

    # All
]

urlpatterns = format_suffix_patterns(urlpatterns)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

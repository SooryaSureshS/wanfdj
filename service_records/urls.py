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
from service_records.views import GetServiceList, GetServiceForm, ServiceStatusUpdate
from service_records.views import ServiceDisapprovalReasonUpdate, GetStudentServiceList
from service_records.views import GetStudentServiceForm, StudentServiceRecordShareToCanteen
from service_records.views import StudentCreateServiceRecord, AppreciateRecord, ServiceRecordDelete
from service_records.views import GetServiceHome, GetServiceSchool, GetServiceCommunity
from service_records.views import GetOtherStudentServiceList, FailRecord, GetStudentServiceOverview
from service_records.views import HomePageOverview, ServiceRecord, GetMissionNotification, ImportRecord, ReportFilter

urlpatterns = [
    # Admin
    path('', ServiceRecord.as_view(), name='Service Record'),
    path('delete', ServiceRecordDelete.as_view(), name='Get Service List'),
    path('get/service/list', GetServiceList.as_view(), name='Get Service List'),
    path('get/service/form', GetServiceForm.as_view(), name='Get Service Form'),
    path('get/service/home', GetServiceHome.as_view(), name='Get Service Home'),
    path('get/service/school', GetServiceSchool.as_view(), name='Get Service Form'),
    path('get/service/community', GetServiceCommunity.as_view(), name='Get Service Form'),
    path('status/update', ServiceStatusUpdate.as_view(), name='Service Status Update'),
    path('disapprove/reason', ServiceDisapprovalReasonUpdate.as_view(), name='Disapprove Reason Update'),
    path('import', ImportRecord.as_view(), name='Import Record'),
    path('report/filter', ReportFilter.as_view(), name='Report Filter'),

    # Student
    path('student/service/list', GetStudentServiceList.as_view(), name='Student Service List'),
    path('student/service/form', GetStudentServiceForm.as_view(), name='Student Service Item'),
    path('student/share/to/canteen', StudentServiceRecordShareToCanteen.as_view(), name='Share to Canteen'),
    path('student/create/service/record', StudentCreateServiceRecord.as_view(), name='Create Service Record'),
    path('student/appreciate/record', AppreciateRecord.as_view(), name='Appreciate Service Record'),
    path('student/fail/record', FailRecord.as_view(), name='Fail Service Record'),
    path('get/others/records', GetOtherStudentServiceList.as_view(), name='Appreciate Service Record'),
    path('student/service/overview', GetStudentServiceOverview.as_view(), name='Student Service Overview'),
    path('home/page/overview', HomePageOverview.as_view(), name='Home Page Overview'),
    path('notification/mission', GetMissionNotification.as_view(), name='Mission Notification')

    # All
]

urlpatterns = format_suffix_patterns(urlpatterns)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

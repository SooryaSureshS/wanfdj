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
from redeem.views import RedeemAPI, RedeemItemListAPI, RedeemItemFormAPI
from redeem.views import RedeemRecordAPI, RedeemRecordListAPI, RedeemRecordFormAPI
from redeem.views import StudentRedeemList, StudentRedeemApplyRegular, StudentRedeemApplySpecial
from redeem.views import RedeemItemsAPI, RedeemItemsListAPI, RedeemItemsFormAPI, RedeemItem, RegularRedeemItem

urlpatterns = [

    # Admin
    path('redeem', RedeemAPI.as_view(), name='Redeem APIs'),
    path('redeem/item/list', RedeemItemListAPI.as_view(), name='Application Services Filter'),
    path('redeem/item/form', RedeemItemFormAPI.as_view(), name='Application Services Form'),
    path('redeem/record', RedeemRecordAPI.as_view(), name='Redeem Record API'),
    path('redeem/record/list', RedeemRecordListAPI.as_view(), name='Redeem Record API'),
    path('redeem/record/form', RedeemRecordFormAPI.as_view(), name='Redeem Record API'),
    # new changes
    path('redeem/items', RedeemItemsAPI.as_view(), name='Redeem items'),  # new changes
    path('redeem/items/list', RedeemItemsListAPI.as_view(), name='Redeem items list'),
    path('redeem/items/form', RedeemItemsFormAPI.as_view(), name='Redeem items form'),
    path('redeem/item', RedeemItem.as_view(), name='Redeem items form'),
    path('redeem/item/regular', RegularRedeemItem.as_view(), name='Regular Redeem items '),

    # Student
    path('student/redeem/list', StudentRedeemList.as_view(), name='Student Redeem List'),
    path('student/redeem/apply/regular', StudentRedeemApplyRegular.as_view(), name='Student Redeem Apply Regular'),
    path('student/redeem/apply/special', StudentRedeemApplySpecial.as_view(), name='Student Redeem Apply Special'),

    # All
]

urlpatterns = format_suffix_patterns(urlpatterns)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

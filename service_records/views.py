import datetime
from rest_framework import status, generics
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.response import Response
from .serializers import ServicesSerializer, ServiceRecordNotAppreciatedUsersSerializer, AddStudentCreateSerializer
from .models import ServiceRecords, ServiceRecordNotAppreciatedUsers, ServiceRecordAppreciatedUsers
from application_service.serializers import NotificationSerializer
from application_service.models import Notification
from accounts.models import User, Form, Class
from rest_framework.permissions import IsAuthenticated
from .pagination import ServiceRecordsPagination
import math
import pytz
from datetime import datetime, timedelta
from datetime import date
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from datetime import datetime as dt


class ServiceRecordDelete(generics.ListCreateAPIView):
    """
            List and Create Role Settings
        """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = ServicesSerializer
    queryset = ServiceRecords.objects.all().order_by('id')

    def delete(self, request, **kwargs):
        """
            Updates snippets delete
            :param kwargs: Role id
            :return: message
        """
        pk = request.data.get('id')
        snippets = self.queryset.filter(id=pk)
        if snippets:
            snippets.delete()
            return Response({
                "success": True,
                "message": "Successfully Deleted",
                "data": {},
            }, status=status.HTTP_201_CREATED)
        return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class GetServiceList(generics.ListCreateAPIView):
    """
      All Service Records
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ServicesSerializer
    queryset = ServiceRecords.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Get all Service Records
            :param request: Service Records
            :param kwargs: NA
            :return: Service Records
        """
        if not request.user.student_id:
            if request.user.role_id is None:
                return Response({"success": False, "message": "User has no role id set"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not (request.user.role_id.all_privileges or request.user.role_id.records_approval
                    or request.user.role_id.records_approval_home or request.user.role_id.records_approval_school
                    or request.user.role_id.records_approval_community):
                return Response({"success": False, "message": "User has no privilege"},
                                status=status.HTTP_400_BAD_REQUEST)

        service_type = request.data.get('service_type')
        approval_status = request.data.get('approval_status')

        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        paginator = ServiceRecordsPagination()
        page_size = paginator.page_size

        if service_type and approval_status:
            snippets = self.queryset.filter(service_type=service_type, approval_status=approval_status).order_by('id')
        elif service_type:
            snippets = self.queryset.filter(service_type=service_type).order_by('id')
        elif approval_status:
            snippets = self.queryset.filter(approval_status=approval_status).order_by('id')
        else:
            snippets = self.queryset.all()
        service_records = []
        seq_prefix_1 = "00"
        seq_prefix_2 = "0"
        seq_prefix_3 = ""
        sequence_suffix = 1

        if snippets:
            for i in snippets:
                if i.user_id and i.user_id.is_student:
                    sequence_prefix = seq_prefix_1
                    if len(str(sequence_suffix)) > 1:
                        sequence_prefix = seq_prefix_2
                    if len(str(sequence_suffix)) > 2:
                        sequence_prefix = seq_prefix_3
                    seq = sequence_prefix + str(sequence_suffix)
                    class_data = i.user_id.class_id
                    service_vals = {
                        "id": i.id,
                        "sequence": seq,
                        "user_id": i.user_id.id if i.user_id else False,
                        "user_name": i.user_id.user_id if i.user_id else False,
                        "user_english_name": i.user_id.english_name if i.user_id else False,
                        "student_id": i.user_id.student_id if i.user_id else False,
                        "class_no": i.user_id.class_no if i.user_id else False,
                        "class_id": class_data.id if class_data else "",
                        "class_name": class_data.class_name if class_data else "",
                        "service_type": i.service_type if i.service_type else False,
                        "category": i.category if i.category else False,
                        "reflection": i.reflection if i.reflection else False,
                        "is_shared": i.is_shared if i.is_shared else False,
                        "is_active": i.is_active if i.is_active else False,
                        "appreciated_user_1": i.appreciated_user_1.id if i.appreciated_user_1 else False,
                        "appreciated_user_2": i.appreciated_user_2.id if i.appreciated_user_2 else False,
                        "appreciated_user_3": i.appreciated_user_3.id if i.appreciated_user_3 else False,
                        "appreciated_user_1_name": i.appreciated_user_1.english_name if i.appreciated_user_1 else False,
                        "appreciated_user_2_name": i.appreciated_user_2.english_name if i.appreciated_user_2 else False,
                        "appreciated_user_3_name": i.appreciated_user_3.english_name if i.appreciated_user_3 else False,
                        "serving_date": i.serving_date if i.serving_date else False,
                        "serving_from_time": i.serving_from_time if i.serving_from_time else False,
                        "serving_to_time": i.serving_to_time if i.serving_to_time else False,
                        "serving_from_date_time": i.serving_from_date_time if i.serving_from_date_time else False,
                        "serving_to_date_time": i.serving_to_date_time if i.serving_to_date_time else False,
                        "service_duration": i.service_duration if i.service_duration else False,
                        "photo": urls + "/service/records/media/" + str(i.photo) if i.photo else False,
                        "approval_status": i.approval_status if i.approval_status else False,
                        "program_nature": i.program_nature if i.program_nature else False,
                        "service_organization": i.service_organization if i.service_organization else False,
                        "person_in_charge_name": i.person_in_charge_name if i.person_in_charge_name else False,
                        "person_in_charge_contact_no": i.person_in_charge_contact_no if i.person_in_charge_contact_no else False,
                        "created_date": str(i.created_date),
                        "updated_date": str(i.updated_date)
                    }
                    service_records.append(service_vals)
                    sequence_suffix = sequence_suffix + 1
            sorted_service_records = sorted(service_records, key=lambda x: x['sequence'], reverse=True)

            result_page = paginator.paginate_queryset(sorted_service_records, request)
            paginator_data = paginator.get_paginated_response(result_page).data
            if len(sorted_service_records) > 0:
                paginator_data['total_pages'] = math.ceil(len(sorted_service_records) / page_size)
            else:
                return Response({"success": False, "message": "No data"},
                                status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "success": True,
                "message": "Success",
                "data": paginator_data,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class GetOtherStudentServiceList(generics.ListCreateAPIView):
    """
      Home Service Records
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ServicesSerializer
    queryset = ServiceRecords.objects.all().order_by('id')

    def post(self, request, *args, **kwargs):
        """
            Get all Service Records
            :param request: Service Records
            :param kwargs: NA
            :return: Service Records
        """
        user_id = request.data.get('user_id')
        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        snippets = self.queryset.filter(service_type='home', is_shared=True, created_date__date=date.today(),
                                        is_active=True).exclude(user_id=user_id)
        service_records = []
        user_val = User.objects.get(id=user_id)
        if snippets:
            for i in snippets:
                if i.user_id and i.user_id.is_student:
                    is_endorsed = False
                    if user_val.user_id in [i.appreciated_user_1.user_id if i.appreciated_user_1 else None,
                                            i.appreciated_user_2.user_id if i.appreciated_user_2 else None,
                                            i.appreciated_user_3.user_id if i.appreciated_user_3 else None]:
                        is_endorsed = True
                    # fail_recs = ServiceRecordNotAppreciatedUsers.objects.filter(user_id=user_id,
                    #                                                             service_record_id=i.id)
                    # if not fail_recs:

                    service_vals = {
                        "id": i.id,
                        "user_id": i.user_id.id if i.user_id else False,
                        "user_name": i.user_id.user_id if i.user_id else False,
                        "user_english_name": i.user_id.english_name if i.user_id else False,
                        "student_id": i.user_id.student_id if i.user_id else False,
                        "class_no": i.user_id.class_no if i.user_id else False,
                        "class_id": i.user_id.class_id.id if i.user_id.class_id else "",
                        "class_name": i.user_id.class_id.class_name if i.user_id.class_id else "",
                        "service_type": i.service_type if i.service_type else False,
                        "category": i.category if i.category else "",
                        "reflection": i.reflection if i.reflection else False,
                        "is_shared": i.is_shared if i.is_shared else False,
                        "is_active": i.is_active if i.is_active else False,
                        "appreciated_user_1": i.appreciated_user_1.id if i.appreciated_user_1 else False,
                        "appreciated_user_2": i.appreciated_user_2.id if i.appreciated_user_2 else False,
                        "appreciated_user_3": i.appreciated_user_3.id if i.appreciated_user_3 else False,
                        "appreciated_user_1_name": i.appreciated_user_1.english_name if i.appreciated_user_1 else False,
                        "appreciated_user_2_name": i.appreciated_user_2.english_name if i.appreciated_user_2 else False,
                        "appreciated_user_3_name": i.appreciated_user_3.english_name if i.appreciated_user_3 else False,
                        "serving_date": i.serving_date if i.serving_date else "",
                        "serving_from_time": i.serving_from_time if i.serving_from_time else False,
                        "serving_to_time": i.serving_to_time if i.serving_to_time else False,
                        "serving_from_date_time": i.serving_from_date_time if i.serving_from_date_time else False,
                        "serving_to_date_time": i.serving_to_date_time if i.serving_to_date_time else False,
                        "service_duration": i.service_duration if i.service_duration else "",
                        "photo": urls + "/service/records/media/" + str(i.photo) if i.photo else "",
                        "approval_status": i.approval_status if i.approval_status else False,
                        "program_nature": i.program_nature if i.program_nature else False,
                        "service_organization": i.service_organization if i.service_organization else False,
                        "person_in_charge_name": i.person_in_charge_name if i.person_in_charge_name else False,
                        "person_in_charge_contact_no": i.person_in_charge_contact_no if i.person_in_charge_contact_no else False,
                        "created_date": str(i.created_date),
                        "updated_date": str(i.updated_date),
                        "is_endorsed": is_endorsed
                    }
                    service_records.append(service_vals)
            sorted_service_records = sorted(service_records, key=lambda x: x['is_endorsed'] is False)
            if service_records:
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": sorted_service_records,
                }, status=status.HTTP_200_OK)

            else:
                return Response({"success": False, "message": "Not Found", "data": {}},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class GetServiceHome(generics.ListCreateAPIView):
    """
      Home Service Records
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ServicesSerializer
    queryset = ServiceRecords.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Get all Service Records
            :param request: Service Records
            :param kwargs: NA
            :return: Service Records
        """
        if not request.user.student_id:
            if request.user.role_id is None:
                return Response({"success": False, "message": "User has no role id set"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not (request.user.role_id.all_privileges or request.user.role_id.monitoring or request.user.role_id.monitoring_home_service):
                return Response({"success": False, "message": "User has no privilege"},
                                status=status.HTTP_400_BAD_REQUEST)

        service_date = request.data.get('service_date')
        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        paginator = ServiceRecordsPagination()
        page_size = paginator.page_size
        if service_date:
            snippets = self.queryset.filter(service_type='home', serving_date=service_date).order_by('id')
        else:
            snippets = self.queryset.filter(service_type='home')
        service_records = []
        seq_prefix_1 = "00"
        seq_prefix_2 = "0"
        seq_prefix_3 = ""
        sequence_suffix = 1

        if snippets:
            for i in snippets:
                if i.user_id and i.user_id.is_student:
                    sequence_prefix = seq_prefix_1
                    if len(str(sequence_suffix)) > 1:
                        sequence_prefix = seq_prefix_2
                    if len(str(sequence_suffix)) > 2:
                        sequence_prefix = seq_prefix_3
                    seq = sequence_prefix + str(sequence_suffix)
                    service_vals = {
                        "id": i.id,
                        "sequence": seq,
                        "user_id": i.user_id.id if i.user_id else False,
                        "user_name": i.user_id.user_id if i.user_id else False,
                        "user_english_name": i.user_id.english_name if i.user_id else False,
                        "student_id": i.user_id.student_id if i.user_id else False,
                        "class_no": i.user_id.class_no if i.user_id else False,
                        "class_id": i.user_id.class_id.id if i.user_id.class_id else "",
                        "class_name": i.user_id.class_id.class_name if i.user_id.class_id else "",
                        "service_type": i.service_type if i.service_type else False,
                        "category": i.category if i.category else False,
                        "reflection": i.reflection if i.reflection else False,
                        "is_shared": i.is_shared if i.is_shared else False,
                        "is_active": i.is_active if i.is_active else False,
                        "appreciated_user_1": i.appreciated_user_1.id if i.appreciated_user_1 else False,
                        "appreciated_user_2": i.appreciated_user_2.id if i.appreciated_user_2 else False,
                        "appreciated_user_3": i.appreciated_user_3.id if i.appreciated_user_3 else False,
                        "appreciated_user_1_name": i.appreciated_user_1.english_name if i.appreciated_user_1 else False,
                        "appreciated_user_2_name": i.appreciated_user_2.english_name if i.appreciated_user_2 else False,
                        "appreciated_user_3_name": i.appreciated_user_3.english_name if i.appreciated_user_3 else False,
                        "serving_date": i.serving_date if i.serving_date else False,
                        "serving_from_time": i.serving_from_time if i.serving_from_time else False,
                        "serving_to_time": i.serving_to_time if i.serving_to_time else False,
                        "serving_from_date_time": i.serving_from_date_time if i.serving_from_date_time else False,
                        "serving_to_date_time": i.serving_to_date_time if i.serving_to_date_time else False,
                        "service_duration": i.service_duration if i.service_duration else False,
                        "photo": urls + "/service/records/media/" + str(i.photo) if i.photo else False,
                        "approval_status": i.approval_status if i.approval_status else False,
                        "program_nature": i.program_nature if i.program_nature else False,
                        "service_organization": i.service_organization if i.service_organization else False,
                        "person_in_charge_name": i.person_in_charge_name if i.person_in_charge_name else False,
                        "person_in_charge_contact_no": i.person_in_charge_contact_no if i.person_in_charge_contact_no else False,
                        "created_date": str(i.created_date),
                        "updated_date": str(i.updated_date)
                    }
                    service_records.append(service_vals)
                    sequence_suffix = sequence_suffix + 1

            result_page = paginator.paginate_queryset(service_records, request)
            paginator_data = paginator.get_paginated_response(result_page).data

            if len(service_records) > 0:
                paginator_data['total_pages'] = math.ceil(len(service_records) / page_size)
            else:
                return Response({"success": False, "message": "No data"},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({
                "success": True,
                "message": "Success",
                "data": paginator_data,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class GetServiceSchool(generics.ListCreateAPIView):
    """
      Home Service Records
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ServicesSerializer
    queryset = ServiceRecords.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Get all Service Records
            :param request: Service Records
            :param kwargs: NA
            :return: Service Records
        """
        if not request.user.student_id:
            if request.user.role_id is None:
                return Response({"success": False, "message": "User has no role id set"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not (request.user.role_id.all_privileges or request.user.role_id.service_record):
                return Response({"success": False, "message": "User has no privilege"},
                                status=status.HTTP_400_BAD_REQUEST)

        service_date = request.data.get('service_date')
        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        if service_date:
            snippets = self.queryset.filter(service_type='school', serving_date=service_date).order_by('id')
        else:
            snippets = self.queryset.filter(service_type='school')
        service_records = []
        seq_prefix_1 = "00"
        seq_prefix_2 = "0"
        seq_prefix_3 = ""
        sequence_suffix = 1

        if snippets:
            for i in snippets:
                if i.user_id and i.user_id.is_student:
                    sequence_prefix = seq_prefix_1
                    if len(str(sequence_suffix)) > 1:
                        sequence_prefix = seq_prefix_2
                    if len(str(sequence_suffix)) > 2:
                        sequence_prefix = seq_prefix_3
                    seq = sequence_prefix + str(sequence_suffix)
                    service_vals = {
                        "id": i.id,
                        "sequence": seq,
                        "user_id": i.user_id.id if i.user_id else False,
                        "user_name": i.user_id.user_id if i.user_id else False,
                        "user_english_name": i.user_id.english_name if i.user_id else False,
                        "student_id": i.user_id.student_id if i.user_id else False,
                        "class_no": i.user_id.class_no if i.user_id else False,
                        "class_id": i.user_id.class_id.id if i.user_id.class_id else "",
                        "class_name": i.user_id.class_id.class_name if i.user_id.class_id else "",
                        "service_type": i.service_type if i.service_type else False,
                        "category": i.category if i.category else False,
                        "reflection": i.reflection if i.reflection else False,
                        "is_shared": i.is_shared if i.is_shared else False,
                        "is_active": i.is_active if i.is_active else False,
                        "appreciated_user_1": i.appreciated_user_1.id if i.appreciated_user_1 else False,
                        "appreciated_user_2": i.appreciated_user_2.id if i.appreciated_user_2 else False,
                        "appreciated_user_3": i.appreciated_user_3.id if i.appreciated_user_3 else False,
                        "appreciated_user_1_name": i.appreciated_user_1.english_name if i.appreciated_user_1 else False,
                        "appreciated_user_2_name": i.appreciated_user_2.english_name if i.appreciated_user_2 else False,
                        "appreciated_user_3_name": i.appreciated_user_3.english_name if i.appreciated_user_3 else False,
                        "serving_date": i.serving_date if i.serving_date else False,
                        "serving_from_time": i.serving_from_time if i.serving_from_time else False,
                        "serving_to_time": i.serving_to_time if i.serving_to_time else False,
                        "serving_from_date_time": i.serving_from_date_time if i.serving_from_date_time else False,
                        "serving_to_date_time": i.serving_to_date_time if i.serving_to_date_time else False,
                        "service_duration": i.service_duration if i.service_duration else False,
                        "photo": urls + "/service/records/media/" + str(i.photo) if i.photo else False,
                        "approval_status": i.approval_status if i.approval_status else False,
                        "program_nature": i.program_nature if i.program_nature else False,
                        "service_organization": i.service_organization if i.service_organization else False,
                        "person_in_charge_name": i.person_in_charge_name if i.person_in_charge_name else False,
                        "person_in_charge_contact_no": i.person_in_charge_contact_no if i.person_in_charge_contact_no else False,
                        "created_date": str(i.created_date),
                        "updated_date": str(i.updated_date)
                    }
                    service_records.append(service_vals)
                    sequence_suffix = sequence_suffix + 1
            return Response({
                "success": True,
                "message": "Success",
                "data": service_records,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class GetServiceCommunity(generics.ListCreateAPIView):
    """
      Home Service Records
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ServicesSerializer
    queryset = ServiceRecords.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Get all Service Records
            :param request: Service Records
            :param kwargs: NA
            :return: Service Records
        """
        if not request.user.student_id:
            if request.user.role_id is None:
                return Response({"success": False, "message": "User has no role id set"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not (request.user.role_id.all_privileges or request.user.role_id.monitoring or request.user.role_id.monitoring_share_record_area):
                return Response({"success": False, "message": "User has no privilege"},
                                status=status.HTTP_400_BAD_REQUEST)

        service_date = request.data.get('service_date')
        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        paginator = ServiceRecordsPagination()
        page_size = paginator.page_size

        if service_date:
            snippets = self.queryset.filter(service_type='community', serving_date=service_date).order_by('id')
        else:
            snippets = self.queryset.filter(service_type='community')
        service_records = []
        seq_prefix_1 = "00"
        seq_prefix_2 = "0"
        seq_prefix_3 = ""
        sequence_suffix = 1

        if snippets:
            for i in snippets:
                if i.user_id and i.user_id.is_student:
                    sequence_prefix = seq_prefix_1
                    if len(str(sequence_suffix)) > 1:
                        sequence_prefix = seq_prefix_2
                    if len(str(sequence_suffix)) > 2:
                        sequence_prefix = seq_prefix_3
                    seq = sequence_prefix + str(sequence_suffix)
                    service_vals = {
                        "id": i.id,
                        "sequence": seq,
                        "user_id": i.user_id.id if i.user_id else False,
                        "user_name": i.user_id.user_id if i.user_id else False,
                        "user_english_name": i.user_id.english_name if i.user_id else False,
                        "student_id": i.user_id.student_id if i.user_id else False,
                        "class_no": i.user_id.class_no if i.user_id else False,
                        "class_id": i.user_id.class_id.id if i.user_id.class_id else "",
                        "class_name": i.user_id.class_id.class_name if i.user_id.class_id else "",
                        "service_type": i.service_type if i.service_type else False,
                        "category": i.category if i.category else False,
                        "reflection": i.reflection if i.reflection else False,
                        "is_shared": i.is_shared if i.is_shared else False,
                        "is_active": i.is_active if i.is_active else False,
                        "appreciated_user_1": i.appreciated_user_1.id if i.appreciated_user_1 else False,
                        "appreciated_user_2": i.appreciated_user_2.id if i.appreciated_user_2 else False,
                        "appreciated_user_3": i.appreciated_user_3.id if i.appreciated_user_3 else False,
                        "appreciated_user_1_name": i.appreciated_user_1.english_name if i.appreciated_user_1 else False,
                        "appreciated_user_2_name": i.appreciated_user_2.english_name if i.appreciated_user_2 else False,
                        "appreciated_user_3_name": i.appreciated_user_3.english_name if i.appreciated_user_3 else False,
                        "serving_date": i.serving_date if i.serving_date else False,
                        "serving_from_time": i.serving_from_time if i.serving_from_time else False,
                        "serving_to_time": i.serving_to_time if i.serving_to_time else False,
                        "serving_from_date_time": i.serving_from_date_time if i.serving_from_date_time else False,
                        "serving_to_date_time": i.serving_to_date_time if i.serving_to_date_time else False,
                        "service_duration": i.service_duration if i.service_duration else False,
                        "photo": urls + "/service/records/media/" + str(i.photo) if i.photo else False,
                        "approval_status": i.approval_status if i.approval_status else False,
                        "program_nature": i.program_nature if i.program_nature else False,
                        "service_organization": i.service_organization if i.service_organization else False,
                        "person_in_charge_name": i.person_in_charge_name if i.person_in_charge_name else False,
                        "person_in_charge_contact_no": i.person_in_charge_contact_no if i.person_in_charge_contact_no else False,
                        "created_date": str(i.created_date),
                        "updated_date": str(i.updated_date)
                    }
                    service_records.append(service_vals)
                    sequence_suffix = sequence_suffix + 1

            result_page = paginator.paginate_queryset(service_records, request)
            paginator_data = paginator.get_paginated_response(result_page).data

            if len(service_records) > 0:
                paginator_data['total_pages'] = math.ceil(len(service_records) / page_size)
            else:
                return Response({"success": False, "message": "No data"},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({
                "success": True,
                "message": "Success",
                "data": paginator_data,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class GetServiceForm(generics.ListCreateAPIView):
    """
        Get Single Service Record
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ServicesSerializer
    queryset = ServiceRecords.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Get single Service Record
            :param request: Service Record id
            :param kwargs: NA
            :return: Specific Service Record
        """
        if not request.user.student_id:
            if request.user.role_id is None:
                return Response({"success": False, "message": "User has no role id set"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not (request.user.role_id.all_privileges or request.user.role_id.records_approval
                    or request.user.role_id.records_approval_home or request.user.role_id.records_approval_school
                    or request.user.role_id.records_approval_community):
                return Response({"success": False, "message": "User has no privilege"},
                                status=status.HTTP_400_BAD_REQUEST)

        service_record_id = request.data.get('id')
        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        if service_record_id:
            snippets = self.queryset.filter(id=service_record_id)
            if snippets:
                for i in snippets:
                    if i.user_id.is_student:
                        class_data = i.user_id.class_id

                        service_vals = {
                            "id": i.id,
                            "user_id": i.user_id.id if i.user_id else False,
                            "user_name": i.user_id.user_id if i.user_id else False,
                            "user_english_name": i.user_id.english_name if i.user_id else False,
                            "student_id": i.user_id.student_id if i.user_id else False,
                            "class_no": i.user_id.class_no if i.user_id else False,
                            "class_id": class_data.id if class_data else False,
                            "class_name": class_data.class_name if class_data else False,
                            "service_type": i.service_type if i.service_type else False,
                            "category": i.category if i.category else False,
                            "reflection": i.reflection if i.reflection else False,
                            "is_shared": i.is_shared if i.is_shared else False,
                            "is_active": i.is_active if i.is_active else False,
                            "appreciated_user_1": i.appreciated_user_1.id if i.appreciated_user_1 else False,
                            "appreciated_user_2": i.appreciated_user_2.id if i.appreciated_user_2 else False,
                            "appreciated_user_3": i.appreciated_user_3.id if i.appreciated_user_3 else False,
                            "appreciated_user_1_name": i.appreciated_user_1.english_name if i.appreciated_user_1 else False,
                            "appreciated_user_2_name": i.appreciated_user_2.english_name if i.appreciated_user_2 else False,
                            "appreciated_user_3_name": i.appreciated_user_3.english_name if i.appreciated_user_3 else False,
                            "serving_date": i.serving_date if i.serving_date else False,
                            "serving_from_time": i.serving_from_time if i.serving_from_time else False,
                            "serving_to_time": i.serving_to_time if i.serving_to_time else False,
                            "serving_from_date_time": i.serving_from_date_time if i.serving_from_date_time else False,
                            "serving_to_date_time": i.serving_to_date_time if i.serving_to_date_time else False,
                            "service_duration": i.service_duration if i.service_duration else False,
                            "photo": urls + "/service/records/media/" + str(i.photo) if i.photo else False,
                            "approval_status": i.approval_status if i.approval_status else False,
                            "program_nature": i.program_nature if i.program_nature else False,
                            "service_organization": i.service_organization if i.service_organization else False,
                            "person_in_charge_name": i.person_in_charge_name if i.person_in_charge_name else False,
                            "person_in_charge_contact_no": i.person_in_charge_contact_no if i.person_in_charge_contact_no else False,
                            "teacher_in_charge_name": i.teacher_in_charge_name if i.teacher_in_charge_name else False,
                            "teacher_in_charge_contact_no": i.teacher_in_charge_contact_no if i.teacher_in_charge_contact_no else False,
                            "created_date": str(i.created_date),
                            "updated_date": str(i.updated_date),
                            "disapproval_date": str(i.disapproval_date),
                        }
                        return Response({
                            "success": True,
                            "message": "Success",
                            "data": service_vals,
                        }, status=status.HTTP_200_OK)
                    else:
                        return Response({
                            "success": True,
                            "message": "Not Found",
                            "data": {},
                        }, status=status.HTTP_200_OK)

            else:
                return Response({"success": False, "message": "Not Found", "data": {}},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class ServiceStatusUpdate(generics.ListCreateAPIView):
    """
        Service Record Status Update
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = ServicesSerializer
    queryset = ServiceRecords.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Service Status Update
            :param request: Service Record id
            :param kwargs: NA
            :return: Update status
        """
        if not request.user.student_id:
            if request.user.role_id is None:
                return Response({"success": False, "message": "User has no role id set"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not (request.user.role_id.all_privileges or request.user.role_id.monitoring or request.user.role_id.monitoring_home_service or request.user.role_id.monitoring_share_record_area):
                return Response({"success": False, "message": "User has no privilege"},
                                status=status.HTTP_400_BAD_REQUEST)

        service_record_id = request.data.get('id')
        service_record_status = request.data.get('approval_status')
        is_active = request.data.get('is_active')

        if service_record_id:
            data = ServiceRecords.objects.filter(id=service_record_id).first()
            user_data = User.objects.get(id=data.user_id.id)
            if data:
                if service_record_status:
                    data.approval_status = service_record_status
                if is_active:
                    data.is_active = is_active
                if service_record_status == "approved" and data.service_type in ['home', 'community', 'school']:
                    if data.service_type == 'home':
                        user_login_points = user_data.login_points + 10
                        user_data.login_points = user_login_points
                    elif data.service_type == 'school':
                        user_student_rubies = user_data.student_rubies + 2
                        user_data.student_rubies = user_student_rubies
                        if service_record_status == "approved" and data.teacher_approved is True:
                            data.is_shared = True
                            # user_value_school = User.objects.get(id=data.user_id.id)
                            # current_coins = user_value_school.login_points
                            # updated_coins = current_coins + 10
                            # user_value_school.login_points = updated_coins
                            # user_value_school.save()

                    elif data.service_type == 'community':
                        user_login_points = user_data.login_points + 30
                        user_student_rubies = user_data.student_rubies + 5
                        user_data.login_points = user_login_points
                        user_data.student_rubies = user_student_rubies
                        if service_record_status == "approved" and data.teacher_approved is True:
                            data.is_shared = True
                            # user_value_community = User.objects.get(id=data.user_id.id)
                            # current_coins = user_value_community.login_points
                            # updated_coins = current_coins + 10
                            # user_value_community.login_points = updated_coins
                            # user_value_community.save()

                elif service_record_status == "disapproved":
                    if (data.service_type == 'school') or (data.service_type == 'community'):
                        data.disapproval_status = True
                        data.counter = data.counter + 1
                        data.save()
                        # time = pytz.timezone('Asia/Hong_kong')
                        # qwer = datetime.now().astimezone(pytz.timezone('Asia/Hong_kong'))
                        # print(qwer)
                        # print(time)
                        # data.disapproval_date = datetime.now(pytz.timezone('Asia/Hong_kong'))
                        # print(datetime.now(pytz.timezone('Asia/Hong_kong')))
                        data.disapproval_date = datetime.now()

                v = data.save()
                if service_record_status == "approved":
                    user = user_data.save()
                    if data.teacher_approved is True:
                        user_value = User.objects.get(id=data.user_id.id)
                        user_login_points = user_value.login_points + 10
                        user_value.login_points = user_login_points
                        user_value.save()
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": "Updated",
                }, status=status.HTTP_200_OK)

            else:
                return Response({"success": False, "message": "Not Found", "data": {}},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"success": False, "message": "Not Found",
                             "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class ServiceDisapprovalReasonUpdate(generics.ListCreateAPIView):
    """
        Service Disapproval Reason Update
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = ServicesSerializer
    queryset = ServiceRecords.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Service Disapproval Reason Update
            :param request: Service Records
            :param kwargs: NA
            :return: Update status
        """
        try:
            if not request.user.student_id:
                if request.user.role_id is None:
                    return Response({"success": False, "message": "User has no role id set"},
                                    status=status.HTTP_400_BAD_REQUEST)
                if not (request.user.role_id.all_privileges or request.user.role_id.records_approval
                        or request.user.role_id.records_approval_home or request.user.role_id.records_approval_school
                        or request.user.role_id.records_approval_community):
                    return Response({"success": False, "message": "User has no privilege"},
                                    status=status.HTTP_400_BAD_REQUEST)

            service_record_id = request.data.get('id')
            disapproval_reason = request.data.get('disapproval_reason')
            if service_record_id and disapproval_reason:
                data = ServiceRecords.objects.get(id=service_record_id)
                if data:
                    data.disapproval_reason = disapproval_reason
                    v = data.save()
                    return Response({
                        "success": True,
                        "message": "Success",
                        "data": "Updated",
                    }, status=status.HTTP_200_OK)

                else:
                    return Response({"success": False, "message": "Not Found", "data": {}},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"success": False, "message": "Not Found",
                                 "data": {}},
                                status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"success": False, "message": "Not Found",
                             "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class GetStudentServiceList(generics.ListCreateAPIView):
    """
        Get Student Service List
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ServicesSerializer
    queryset = ServiceRecords.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Student Service Records
            :param request: Student id
            :param kwargs: NA
            :return: Service Records
        """
        user_id = request.data.get('user_id')

        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)
        user_data = User.objects.filter(id=user_id).first()
        if not user_data:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)
        snippets = self.queryset.filter(user_id=user_data).order_by('-id')

        shared_records = []
        private_records = []
        if snippets:
            for i in snippets:
                appreciated_count = 0
                if i.appreciated_user_1 is not None:
                    appreciated_count = appreciated_count + 1
                if i.appreciated_user_2 is not None:
                    appreciated_count = appreciated_count + 1
                if i.appreciated_user_3 is not None:
                    appreciated_count = appreciated_count + 1
                if i.user_id and i.user_id.is_student:
                    if i.is_shared:
                        shared_service_vals = {
                            "id": i.id,
                            "user_id": i.user_id.id if i.user_id else "",
                            "user_name": i.user_id.user_id if i.user_id else "",
                            "user_english_name": i.user_id.english_name if i.user_id else "",
                            "student_id": i.user_id.student_id if i.user_id else "",
                            "class_no": i.user_id.class_no if i.user_id else "",
                            "class_id": i.user_id.class_id.id if i.user_id.class_id else "",
                            "class_name": i.user_id.class_id.class_name if i.user_id.class_id else "",
                            "service_type": i.service_type if i.service_type else "",
                            "category": i.category if i.category else "",
                            "reflection": i.reflection if i.reflection else "",
                            "is_shared": i.is_shared if i.is_shared else False,
                            "is_active": i.is_active if i.is_active else False,
                            "appreciated_user_1": i.appreciated_user_1.id if i.appreciated_user_1 else "",
                            "appreciated_user_2": i.appreciated_user_2.id if i.appreciated_user_2 else "",
                            "appreciated_user_3": i.appreciated_user_3.id if i.appreciated_user_3 else "",
                            "appreciated_user_1_name": i.appreciated_user_1.english_name if i.appreciated_user_1 else "",
                            "appreciated_user_2_name": i.appreciated_user_2.english_name if i.appreciated_user_2 else "",
                            "appreciated_user_3_name": i.appreciated_user_3.english_name if i.appreciated_user_3 else "",
                            "serving_date": i.serving_date if i.serving_date else "",
                            "serving_from_time": i.serving_from_time if i.serving_from_time else "",
                            "serving_to_time": i.serving_to_time if i.serving_to_time else "",
                            "serving_from_date_time": i.serving_from_date_time if i.serving_from_date_time else "",
                            "serving_to_date_time": i.serving_to_date_time if i.serving_to_date_time else "",
                            "service_duration": i.service_duration if i.service_duration else "",
                            "photo": urls + "/service/records/media/" + str(i.photo) if i.photo else "null",
                            "approval_status": i.approval_status if i.approval_status else "",
                            "program_nature": i.program_nature if i.program_nature else False,
                            "service_organization": i.service_organization if i.service_organization else "",
                            "person_in_charge_name": i.person_in_charge_name if i.person_in_charge_name else "",
                            "person_in_charge_contact_no": i.person_in_charge_contact_no if i.person_in_charge_contact_no else "",
                            "created_date": str(i.created_date),
                            "updated_date": str(i.updated_date),
                            "teacher_approved": i.teacher_approved if i.teacher_approved else False,
                            "disapproval_reason": i.disapproval_reason if i.disapproval_reason else "",
                            "disapproval_status": i.disapproval_status if i.disapproval_status else False,
                            "counter": i.counter if i.counter else "0",
                            "disapproval_date": str(i.disapproval_date),
                            "appreciated_count": appreciated_count
                        }
                        shared_records.append(shared_service_vals)
                    else:
                        private_service_vals = {
                            "id": i.id,
                            "user_id": i.user_id.id if i.user_id else "",
                            "user_name": i.user_id.user_id if i.user_id else "",
                            "user_english_name": i.user_id.english_name if i.user_id else "",
                            "student_id": i.user_id.student_id if i.user_id else "",
                            "class_no": i.user_id.class_no if i.user_id else "",
                            "class_id": i.user_id.class_id.id if i.user_id.class_id else "",
                            "class_name": i.user_id.class_id.class_name if i.user_id.class_id else "",
                            "service_type": i.service_type if i.service_type else "",
                            "category": i.category if i.category else "",
                            "reflection": i.reflection if i.reflection else "",
                            "is_shared": i.is_shared if i.is_shared else False,
                            "is_active": i.is_active if i.is_active else False,
                            "appreciated_user_1": i.appreciated_user_1.id if i.appreciated_user_1 else "",
                            "appreciated_user_2": i.appreciated_user_2.id if i.appreciated_user_2 else "",
                            "appreciated_user_3": i.appreciated_user_3.id if i.appreciated_user_3 else "",
                            "appreciated_user_1_name": i.appreciated_user_1.english_name if i.appreciated_user_1 else "",
                            "appreciated_user_2_name": i.appreciated_user_2.english_name if i.appreciated_user_2 else "",
                            "appreciated_user_3_name": i.appreciated_user_3.english_name if i.appreciated_user_3 else "",
                            "serving_date": i.serving_date if i.serving_date else "",
                            "serving_from_time": i.serving_from_time if i.serving_from_time else "",
                            "serving_to_time": i.serving_to_time if i.serving_to_time else "",
                            "serving_from_date_time": i.serving_from_date_time if i.serving_from_date_time else "",
                            "serving_to_date_time": i.serving_to_date_time if i.serving_to_date_time else "",
                            "service_duration": i.service_duration if i.service_duration else "",
                            "photo": urls + "/service/records/media/" + str(i.photo) if i.photo else "null",
                            "approval_status": i.approval_status if i.approval_status else "",
                            "program_nature": i.program_nature if i.program_nature else "",
                            "service_organization": i.service_organization if i.service_organization else "",
                            "person_in_charge_name": i.person_in_charge_name if i.person_in_charge_name else "",
                            "person_in_charge_contact_no": i.person_in_charge_contact_no if i.person_in_charge_contact_no else "",
                            "created_date": str(i.created_date),
                            "updated_date": str(i.updated_date),
                            "teacher_approved": i.teacher_approved if i.teacher_approved else False,
                            "disapproval_reason": i.disapproval_reason if i.disapproval_reason else "",
                            "disapproval_status": i.disapproval_status if i.disapproval_status else False,
                            "counter": i.counter if i.counter else "0",
                            "disapproval_date": str(i.disapproval_date),
                            "appreciated_count": appreciated_count
                        }
                        private_records.append(private_service_vals)
                else:
                    return Response({"success": False, "message": "Not Found", "data": {}},
                                    status=status.HTTP_400_BAD_REQUEST)
            service_records = {
                "shared_record_count": len(shared_records),
                "shared_records": shared_records,
                "private_record_count": len(private_records),
                "private_records": private_records,
            }
            return Response({
                "success": True,
                "message": "Success",
                "data": service_records,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class GetStudentServiceForm(generics.ListCreateAPIView):
    """
        Get Single Service Record
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ServicesSerializer
    queryset = ServiceRecords.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Student single Service Record
            :param request: Service Record id
            :param kwargs: NA
            :return: Specific Service Record
        """
        service_record_id = request.data.get('id')
        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        appreciated_count = 0

        if service_record_id:
            snippets = self.queryset.filter(id=service_record_id)
            if snippets:
                for i in snippets:
                    if i.appreciated_user_1 is not None:
                        appreciated_count = appreciated_count + 1
                    if i.appreciated_user_2 is not None:
                        appreciated_count = appreciated_count + 1
                    if i.appreciated_user_3 is not None:
                        appreciated_count = appreciated_count + 1
                    if i.user_id.is_student:
                        service_vals = {
                            "id": i.id,
                            "user_id": i.user_id.id if i.user_id else "",
                            "user_name": i.user_id.user_id if i.user_id else "",
                            "user_english_name": i.user_id.english_name if i.user_id else "",
                            "student_id": i.user_id.student_id if i.user_id else "",
                            "class_no": i.user_id.class_no if i.user_id else "",
                            "class_id": i.user_id.class_id.id if i.user_id.class_id else "",
                            "class_name": i.user_id.class_id.class_name if i.user_id.class_id else "",
                            "service_type": i.service_type if i.service_type else "",
                            "category": i.category if i.category else "",
                            "reflection": i.reflection if i.reflection else "",
                            "is_shared": i.is_shared if i.is_shared else False,
                            "is_active": i.is_active if i.is_active else False,
                            "appreciated_user_1": i.appreciated_user_1.id if i.appreciated_user_1 else "",
                            "appreciated_user_2": i.appreciated_user_2.id if i.appreciated_user_2 else "",
                            "appreciated_user_3": i.appreciated_user_3.id if i.appreciated_user_3 else "",
                            "appreciated_user_1_name": i.appreciated_user_1.english_name if i.appreciated_user_1 else "",
                            "appreciated_user_2_name": i.appreciated_user_2.english_name if i.appreciated_user_2 else "",
                            "appreciated_user_3_name": i.appreciated_user_3.english_name if i.appreciated_user_3 else "",
                            "serving_date": i.serving_date if i.serving_date else "",
                            "serving_from_time": i.serving_from_time if i.serving_from_time else "",
                            "serving_to_time": i.serving_to_time if i.serving_to_time else "",
                            "serving_from_date_time": i.serving_from_date_time if i.serving_from_date_time else "",
                            "serving_to_date_time": i.serving_to_date_time if i.serving_to_date_time else "",
                            "service_duration": i.service_duration if i.service_duration else "",
                            "photo": urls + "/service/records/media/" + str(i.photo) if i.photo else "",
                            "approval_status": i.approval_status if i.approval_status else "",
                            "program_nature": i.program_nature if i.program_nature else "",
                            "service_organization": i.service_organization if i.service_organization else "",
                            "person_in_charge_name": i.person_in_charge_name if i.person_in_charge_name else "",
                            "person_in_charge_contact_no": i.person_in_charge_contact_no if i.person_in_charge_contact_no else "",
                            "created_date": str(i.created_date),
                            "updated_date": str(i.updated_date),
                            "teacher_approved": i.teacher_approved if i.teacher_approved else False,
                            "disapproval_reason": i.disapproval_reason if i.disapproval_reason else "",
                            "disapproval_status": i.disapproval_status if i.disapproval_status else False,
                            "counter": i.counter if i.counter else "0",
                            "disapproval_date": str(
                                i.disapproval_date + timedelta(hours=8)) if i.disapproval_date else "",
                            "appreciated_count": appreciated_count,
                            "teacher_in_charge_name": i.teacher_in_charge_name if i.teacher_in_charge_name else False,
                            "teacher_in_charge_contact_no": i.teacher_in_charge_contact_no if i.teacher_in_charge_contact_no else False,

                        }
                        return Response({
                            "success": True,
                            "message": "Success",
                            "data": service_vals,
                        }, status=status.HTTP_200_OK)
                    else:
                        return Response({
                            "success": True,
                            "message": "Not Found",
                            "data": {},
                        }, status=status.HTTP_200_OK)

            else:
                return Response({"success": False, "message": "Not Found", "data": {}},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class StudentServiceRecordShareToCanteen(generics.ListCreateAPIView):
    """
        Service Record Share to Canteen
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ServicesSerializer
    queryset = ServiceRecords.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Service Record Share to Canteen
            :param request: Service Record id
            :param kwargs: NA
            :return: Update to canteen
        """
        try:
            service_record_id = request.data.get('id')
            if service_record_id:
                data = ServiceRecords.objects.get(id=service_record_id)
                if data:
                    if data.user_id:
                        data.is_shared = True
                        v = data.save()
                        user_data = User.objects.get(id=data.user_id.id)
                        if user_data:
                            current_coins = user_data.login_points
                            new_coins = current_coins + 10
                            user_data.login_points = new_coins
                            user_data.save()
                        return Response({
                            "success": True,
                            "message": "Success",
                            "data": "Share Success",
                        }, status=status.HTTP_200_OK)

                else:
                    return Response({"success": False, "message": "Not Found", "data": {}},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"success": False, "message": "Not Found",
                                 "data": {}},
                                status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"success": False, "message": "Not Found",
                             "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class StudentCreateServiceRecord(generics.ListCreateAPIView):
    """
        Service Record Share to Canteen
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = ServicesSerializer
    queryset = ServiceRecords.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Create Service Records From Mobile
            :param request: Service Records details
            :param kwargs: NA
            :return: Service Records details
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            if serializer.data.get('is_shared') is True:
                user_data = User.objects.get(id=request.data.get('user_id'))
                if user_data:
                    current_coins = user_data.login_points
                    new_coins = current_coins + 10
                    user_data.login_points = new_coins
                    user_data.save()
            return Response({
                "success": True,
                "message": "Success",
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED)
        return Response({"success": False, "message": "Failed", "data": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class AppreciateRecord(generics.ListCreateAPIView):
    """
        Service Record Share to Canteen
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ServicesSerializer
    queryset = ServiceRecords.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Service Record Share to Canteen
            :param request: Service Record id
            :param kwargs: NA
            :return: Update to canteen
        """
        try:
            service_record_id = request.data.get('service_record_id')
            user_id = request.data.get('user_id')
            user_data = User.objects.get(id=user_id)
            service_endorse_rec = ServiceRecordAppreciatedUsers.objects.filter(user_id=user_data, created_date__date=date.today()).count()
            if int(service_endorse_rec) == 3:
                return Response({
                    "success": False,
                    "message": "You Already Appreciated 3 Times",
                    "data": {},
                }, status=status.HTTP_200_OK)
            if service_record_id:
                data = ServiceRecords.objects.get(id=service_record_id)
                if data:
                    if not request.user.student_id:
                        if request.user.role_id is None:
                            return Response({"success": False, "message": "User has no role id set"},
                                            status=status.HTTP_400_BAD_REQUEST)
                    if not request.user.student_id:
                        if not (request.user.role_id.all_privileges or request.user.role_id.records_approval):
                            if data.service_type == 'community':
                                if not request.user.role_id.records_approval_community:
                                    return Response({"success": False,
                                                     "message": "User has no privilege to approve community record"},
                                                    status=status.HTTP_400_BAD_REQUEST)
                            elif data.service_type == 'school':
                                if not request.user.role_id.records_approval_school:
                                    return Response(
                                        {"success": False, "message": "User has no privilege to approve school record"},
                                        status=status.HTTP_400_BAD_REQUEST)

                    if data.appreciated_user_1 and data.appreciated_user_2 and data.appreciated_user_3:
                        if data.approval_status in ['waiting', 'disapproved']:
                            data.approval_status = "approved"
                            data.save()
                            service_user = data.user_id
                            current_coins = service_user.login_points
                            updated_coins = current_coins + 10
                            service_user.login_points = updated_coins
                            service_user.save()
                        return Response({
                            "success": False,
                            "message": "Already Appreciated by 3 users",
                            "data": {},
                        }, status=status.HTTP_200_OK)
                    if data.user_id.id != user_id:
                        if data.appreciated_user_1 and data.appreciated_user_1.id != user_id:
                            pass
                        elif data.appreciated_user_1 and data.appreciated_user_1.id == user_id:
                            return Response({
                                "success": False,
                                "message": "Already Appreciated",
                                "data": {},
                            }, status=status.HTTP_200_OK)

                        if data.appreciated_user_2 and data.appreciated_user_2.id != user_id:
                            pass
                        if data.appreciated_user_2 and data.appreciated_user_2.id == user_id:
                            return Response({
                                "success": False,
                                "message": "Already Appreciated",
                                "data": {},
                            }, status=status.HTTP_200_OK)
                        if data.appreciated_user_3 and data.appreciated_user_3.id != user_id:
                            pass
                        if data.appreciated_user_3 and data.appreciated_user_3.id == user_id:
                            return Response({
                                "success": False,
                                "message": "Already Appreciated",
                                "data": {},
                            }, status=status.HTTP_200_OK)

                        if not data.appreciated_user_1:
                            data.appreciated_user_1 = user_data
                        elif not data.appreciated_user_2:
                            data.appreciated_user_2 = user_data
                        elif not data.appreciated_user_3:
                            data.appreciated_user_3 = user_data
                            if data.approval_status in ['waiting', 'disapproved']:
                                data.approval_status = "approved"
                                data.save()
                                service_user = data.user_id
                                current_coins = service_user.login_points
                                updated_coins = current_coins + 10
                                service_user.login_points = updated_coins
                                service_user.save()
                        v = data.save()
                        service = ServiceRecordAppreciatedUsers(user_id=user_data, service_record_id=data,
                                                                created_date_val=date.today())
                        service.save()

                        current_coins = user_data.login_points
                        updated_coins = current_coins + 5
                        user_data.login_points = updated_coins

                        # if data.approval_status in ['waiting', 'disapproved']:
                        #     data.approval_status = "approved"
                        #     data.save()
                        #     service_user = data.user_id
                        #     current_coins = service_user.login_points
                        #     updated_coins = current_coins + 10
                        #     service_user.login_points = updated_coins
                        #     service_user.save()

                        user_data.save()
                        return Response({
                            "success": True,
                            "message": "Success",
                            "data": "Appreciated",
                        }, status=status.HTTP_200_OK)
                    else:
                        return Response({
                            "success": False,
                            "message": "Cannot appreciate your own record",
                            "data": {},
                        }, status=status.HTTP_200_OK)
                else:
                    return Response({"success": False, "message": "Not Found", "data": {}},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"success": False, "message": "Not Found",
                                 "data": {}},
                                status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"success": False, "message": "Not Found",
                             "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class FailRecord(generics.ListCreateAPIView):
    """
        Service Record Share to Canteen
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ServiceRecordNotAppreciatedUsersSerializer
    queryset = ServiceRecordNotAppreciatedUsers.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            create Fail Records
            :param request: Role Settings
            :param kwargs: NA
            :return: Role Settings details
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Success",
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED)
        return Response({"success": False, "message": "Failed", "data": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class GetStudentServiceOverview(generics.ListCreateAPIView):
    """
        Service Records
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ServicesSerializer

    def post(self, request):
        try:
            user_id = request.data.get('user_id')
            user_data = User.objects.get(id=user_id)
            current_year = date.today().year
            current_school_service = ServiceRecords.objects.filter(service_type="school", user_id=user_id,
                                                                   created_date__year__gte=current_year,
                                                                   created_date__year__lte=current_year + 1)
            current_home_service = ServiceRecords.objects.filter(service_type="home", user_id=user_id,
                                                                 created_date__year__gte=current_year,
                                                                 created_date__year__lte=current_year + 1)
            current_community_service = ServiceRecords.objects.filter(service_type="community", user_id=user_id,
                                                                      created_date__year__gte=current_year,
                                                                      created_date__year__lte=current_year + 1)
            school_service = ServiceRecords.objects.filter(service_type="school", user_id=user_id,
                                                           created_date__year__gte=current_year - 1,
                                                           created_date__year__lte=current_year + 5)
            home_service = ServiceRecords.objects.filter(service_type="home", user_id=user_id,
                                                         created_date__year__gte=current_year - 1,
                                                         created_date__year__lte=current_year + 5)
            community_service = ServiceRecords.objects.filter(service_type="community", user_id=user_id,
                                                              created_date__year__gte=current_year - 1,
                                                              created_date__year__lte=current_year + 5)

            current_school_service_hrs = 0
            current_home_service_hrs = 0
            current_community_service_hrs = 0

            if current_school_service:
                for i in current_school_service:
                    if i.service_duration:
                        formatted_time = datetime.strptime(i.service_duration, '%H:%M:%S.%f').time()
                        hour_school = formatted_time.hour
                        minute_school = formatted_time.minute
                        school_time = hour_school * 60 + minute_school
                        total_hrs = 0
                        if school_time > 0:
                            total_hrs = school_time / 60
                        current_school_service_hrs = round((current_school_service_hrs + total_hrs), 2)

            if current_home_service:
                for i in current_home_service:
                    if i.service_duration:
                        formatted_time = datetime.strptime(i.service_duration, '%H:%M:%S.%f').time()
                        hour_school = formatted_time.hour
                        minute_school = formatted_time.minute
                        school_time = hour_school * 60 + minute_school
                        total_hrs = 0
                        if school_time > 0:
                            total_hrs = school_time / 60
                        current_home_service_hrs = round((current_home_service_hrs + total_hrs), 2)
            if current_community_service:
                for i in current_community_service:
                    if i.service_duration:
                        formatted_time = datetime.strptime(i.service_duration, '%H:%M:%S.%f').time()
                        hour_school = formatted_time.hour
                        minute_school = formatted_time.minute
                        school_time = hour_school * 60 + minute_school
                        total_hrs = 0
                        if school_time > 0:
                            total_hrs = school_time / 60
                        current_community_service_hrs = round((current_community_service_hrs + total_hrs), 2)

            school_hours = int(current_school_service_hrs)
            school_minutes = int((current_school_service_hrs * 60) % 60)
            current_school_service_hrs_val = str(school_hours) + ":" + str(school_minutes)

            home_hours = int(current_home_service_hrs)
            home_minutes = int((current_home_service_hrs * 60) % 60)
            current_home_service_hrs_val = str(home_hours) + ":" + str(home_minutes)

            community_hours = int(current_community_service_hrs)
            community_minutes = int((current_community_service_hrs * 60) % 60)
            current_community_service_hrs_val = str(community_hours) + ":" + str(community_minutes)

            if current_school_service_hrs == 0:
                current_school_service_hrs_val = "0"
            if current_home_service_hrs == 0:
                current_home_service_hrs_val = "0"
            if current_community_service_hrs == 0:
                current_community_service_hrs_val = "0"

            school_service_hrs = 0
            home_service_hrs = 0
            community_service_hrs = 0

            if school_service:
                for i in school_service:
                    if i.service_duration:
                        formatted_time = datetime.strptime(i.service_duration, '%H:%M:%S.%f').time()
                        hour_school = formatted_time.hour
                        minute_school = formatted_time.minute
                        school_time = hour_school * 60 + minute_school
                        total_hrs = 0
                        if school_time > 0:
                            total_hrs = school_time / 60
                        school_service_hrs = round(school_service_hrs + total_hrs, 2)

            if home_service:
                for i in home_service:
                    if i.service_duration:
                        formatted_time = datetime.strptime(i.service_duration, '%H:%M:%S.%f').time()
                        hour_school = formatted_time.hour
                        minute_school = formatted_time.minute
                        school_time = hour_school * 60 + minute_school
                        total_hrs = 0
                        if school_time > 0:
                            total_hrs = school_time / 60
                        home_service_hrs = round((home_service_hrs + total_hrs), 2)
            if community_service:
                for i in community_service:
                    if i.service_duration:
                        formatted_time = datetime.strptime(i.service_duration, '%H:%M:%S.%f').time()
                        hour_school = formatted_time.hour
                        minute_school = formatted_time.minute
                        school_time = hour_school * 60 + minute_school
                        total_hrs = 0
                        if school_time > 0:
                            total_hrs = school_time / 60
                        community_service_hrs = round((community_service_hrs + total_hrs), 2)

            school_hours = int(school_service_hrs)
            school_minutes = int((school_service_hrs * 60) % 60)
            school_service_hrs_val = str(school_hours) + ":" + str(school_minutes)

            home_hours = int(home_service_hrs)
            home_minutes = int((home_service_hrs * 60) % 60)
            home_service_hrs_val = str(home_hours) + ":" + str(home_minutes)

            community_hours = int(community_service_hrs)
            community_minutes = int((community_service_hrs * 60) % 60)
            community_service_hrs_val = str(community_hours) + ":" + str(community_minutes)

            if school_service_hrs == 0:
                school_service_hrs_val = "0"
            if home_service_hrs == 0:
                home_service_hrs_val = "0"
            if community_service_hrs == 0:
                community_service_hrs_val = "0"

            duration = []
            current_service_duration = {
                "year": f"{current_year} - {current_year + 1}",
                "current_school_service_hrs": current_school_service_hrs_val,
                "current_home_service_hrs": current_home_service_hrs_val,
                "current_community_service_hrs": current_community_service_hrs_val
            }
            duration.append(current_service_duration)
            service_duration = {
                "year": f"{current_year - 1} - {current_year + 5}",
                "school_service_hrs": school_service_hrs_val,
                "home_service_hrs": home_service_hrs_val,
                "community_service_hrs": community_service_hrs_val
            }
            duration.append(service_duration)
            return Response({
                "success": True,
                "message": "Success",
                "results": duration
            }, status=status.HTTP_200_OK)

        except:
            return Response({"success": False, "message": "Not Found",
                             "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class HomePageOverview(generics.ListAPIView):
    """
        Service Records
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ServicesSerializer

    def get(self, request):
        users = User.objects.filter(is_student=True).count()
        home_services = ServiceRecords.objects.filter(service_type='home')
        school_services = ServiceRecords.objects.filter(service_type='school')
        community_services = ServiceRecords.objects.filter(service_type='community')
        home_service_hrs = 0
        for i in home_services:
            if i.service_duration is not None:
                formatted_time = datetime.strptime(i.service_duration, '%H:%M:%S.%f').time()
                hour_school = formatted_time.hour
                minute_school = formatted_time.minute
                school_time = hour_school * 60 + minute_school
                total_hrs = 0
                if school_time > 0:
                    total_hrs = school_time / 60
                home_service_hrs = round((home_service_hrs + total_hrs), 2)
        school_service_hrs = 0
        for i in school_services:
            if i.service_duration is not None:
                formatted_time = datetime.strptime(i.service_duration, '%H:%M:%S.%f').time()
                hour_school = formatted_time.hour
                minute_school = formatted_time.minute
                school_time = hour_school * 60 + minute_school
                total_hrs = 0
                if school_time > 0:
                    total_hrs = school_time / 60
                school_service_hrs = round(school_service_hrs + total_hrs, 2)
        community_service_hrs = 0
        for i in community_services:
            if i.service_duration is not None:
                formatted_time = datetime.strptime(i.service_duration, '%H:%M:%S.%f').time()
                hour_school = formatted_time.hour
                minute_school = formatted_time.minute
                school_time = hour_school * 60 + minute_school
                total_hrs = 0
                if school_time > 0:
                    total_hrs = school_time / 60
                community_service_hrs = round((community_service_hrs + total_hrs), 2)

        school_hours = int(school_service_hrs)
        school_minutes = int((school_service_hrs * 60) % 60)
        school_service_hrs_val = str(school_hours) + ":" + str(school_minutes)

        home_hours = int(home_service_hrs)
        home_minutes = int((home_service_hrs * 60) % 60)
        home_service_hrs_val = str(home_hours) + ":" + str(home_minutes)

        community_hours = int(community_service_hrs)
        community_minutes = int((community_service_hrs * 60) % 60)
        community_service_hrs_val = str(community_hours) + ":" + str(community_minutes)

        if school_service_hrs == 0:
            school_service_hrs_val = "0"
        if home_service_hrs == 0:
            home_service_hrs_val = "0"
        if community_service_hrs == 0:
            community_service_hrs_val = "0"

        overview = {"total_users": users,
                    "home_service_hrs": home_service_hrs_val,
                    "school_service_hrs": school_service_hrs_val,
                    "community_service_hrs": community_service_hrs_val}
        return Response({
            "success": True,
            "message": "Success",
            "results": overview
        }, status=status.HTTP_200_OK)


class ServiceRecord(generics.ListCreateAPIView):
    """
        Service Record
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = ServicesSerializer
    queryset = ServiceRecords.objects.all().order_by('id')

    def get_object(self, pk):
        try:
            return self.queryset.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_user(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        """
            create Redeem
            :param request: Redeem
            :param kwargs: NA
            :return: Redeem details
        """
        serializer = self.serializer_class(data=request.data, context={"user": self.get_user()})
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Success",
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED)
        return Response({"success": False, "message": "Failed", "data": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        """
        Updates snippets delete
        :param kwargs: snippets id
        :return: message
        """
        pk = request.data.get('id')
        snippets = self.queryset.filter(id=pk)
        if snippets:
            snippets.delete()
            return Response({
                "success": True,
                "message": "Successfully Deleted",
                "data": {},
            }, status=status.HTTP_201_CREATED)
        return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, **kwargs):
        """
        Updates snippets delete
        :param kwargs: snippets id
        :return: message
        """
        pk = request.data.get('id')
        snippets = self.get_object(pk)
        serializer = self.serializer_class(instance=snippets, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Success",
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED)
        return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class GetMissionNotification(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ServicesSerializer
    queryset = ServiceRecords.objects.all().order_by('id')
    serializer_class1 = NotificationSerializer
    queryset1 = Notification.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Student Service Records
            :param request: Student id
            :param kwargs: NA
            :return: Service Records
        """
        user_id = request.data.get('user_id')
        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)
        user_data = User.objects.filter(id=user_id).first()
        if not user_data:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)
        snippets = self.queryset.filter(user_id=user_data).order_by('-id')
        snippets1 = self.queryset1.filter(student_id=user_data).order_by('-id')
        records = []
        count = 0
        if snippets or snippets1:
            for i in snippets:
                if i.user_id and i.user_id.is_student:
                    if i.disapproval_status is True and i.counter > 0:
                        service_vals = {
                            "id": i.id,
                            "user_id": i.user_id.id if i.user_id else "",
                            "user_name": i.user_id.user_id if i.user_id else "",
                            "user_english_name": i.user_id.english_name if i.user_id else "",
                            "student_id": i.user_id.student_id if i.user_id else "",
                            "class_no": i.user_id.class_no if i.user_id else "",
                            "class_id": i.user_id.class_id.id if i.user_id.class_id else "",
                            "class_name": i.user_id.class_id.class_name if i.user_id.class_id else "",
                            "service_type": i.service_type if i.service_type else "",
                            "category": i.category if i.category else "",
                            "reflection": i.reflection if i.reflection else "",
                            "is_shared": i.is_shared if i.is_shared else False,
                            "is_active": i.is_active if i.is_active else False,
                            "appreciated_user_1": i.appreciated_user_1.id if i.appreciated_user_1 else "",
                            "appreciated_user_2": i.appreciated_user_2.id if i.appreciated_user_2 else "",
                            "appreciated_user_3": i.appreciated_user_3.id if i.appreciated_user_3 else "",
                            "appreciated_user_1_name": i.appreciated_user_1.english_name if i.appreciated_user_1 else "",
                            "appreciated_user_2_name": i.appreciated_user_2.english_name if i.appreciated_user_2 else "",
                            "appreciated_user_3_name": i.appreciated_user_3.english_name if i.appreciated_user_3 else "",
                            "serving_date": i.serving_date if i.serving_date else "",
                            "serving_from_time": i.serving_from_time if i.serving_from_time else "",
                            "serving_to_time": i.serving_to_time if i.serving_to_time else "",
                            "serving_from_date_time": i.serving_from_date_time if i.serving_from_date_time else "",
                            "serving_to_date_time": i.serving_to_date_time if i.serving_to_date_time else "",
                            "service_duration": i.service_duration if i.service_duration else "",
                            "photo": urls + "/service/records/media/" + str(i.photo) if i.photo else "null",
                            "approval_status": i.approval_status if i.approval_status else "",
                            "program_nature": i.program_nature if i.program_nature else False,
                            "service_organization": i.service_organization if i.service_organization else "",
                            "person_in_charge_name": i.person_in_charge_name if i.person_in_charge_name else "",
                            "person_in_charge_contact_no": i.person_in_charge_contact_no if i.person_in_charge_contact_no else "",
                            "created_date": str(i.created_date),
                            "updated_date": str(i.updated_date),
                            "teacher_approved": i.teacher_approved if i.teacher_approved else False,
                            "disapproval_reason": i.disapproval_reason if i.disapproval_reason else "",
                            "disapproval_status": i.disapproval_status if i.disapproval_status else False,
                            "counter": i.counter if i.counter else "0",
                            "object": "Reasons of disapproval",
                            "notification_opened_status": i.notification_opened_status if i.notification_opened_status else False,
                            "disapproval_date": str(
                                i.disapproval_date + timedelta(hours=8)) if i.disapproval_date else "",

                        }
                        records.append(service_vals)
                        if i.notification_opened_status is False:
                            count = count + 1

            for j in snippets1:
                if j.student_id or j.applicant_service_id:
                    if j.approval_status == 'approved':
                        service_val = {
                            "id": j.id,
                            "user_id": j.student_id.id if j.student_id else "",
                            "user_name": j.student_id.student_id if j.student_id else "",
                            "user_english_name": j.student_id.english_name if j.student_id else "",
                            "student_id": j.student_id.student_id if j.student_id else "",
                            "class_no": j.student_id.class_no if j.student_id else "",
                            "class_id": j.student_id.class_id.id if j.student_id.class_id else "",
                            "class_name": j.student_id.class_id.class_name if j.student_id.class_id else "",
                            "student_contact_no": j.applicant_service_id.student_contact_no if j.applicant_service_id.student_contact_no else "",
                            "parent_contact_no": j.applicant_service_id.parent_contact_no if j.applicant_service_id.parent_contact_no else "",
                            "parent_consent": j.applicant_service_id.parent_consent if j.applicant_service_id.parent_consent else False,
                            "date_of_application": j.applicant_service_id.date_of_application if j.applicant_service_id.date_of_application else "",
                            "approval_status": j.approval_status if j.approval_status else "",
                            "created_date": str(j.created_date),
                            "reminder": j.reminder if j.reminder else "",
                            "object": "Mission approval",
                            "notification_opened_status": j.notification_opened_status if j.notification_opened_status else False,
                            "approval_date": str(j.applicant_service_id.approval_date + timedelta(hours=8)) if j.applicant_service_id.approval_date else "",
                        }
                        records.append(service_val)
                        if j.notification_opened_status is False:
                            count = count + 1
                    elif j.approval_status == 'disapproved':
                        service_val = {
                            "id": j.id,
                            "user_id": j.student_id.id if j.student_id else "",
                            "user_name": j.student_id.student_id if j.student_id else "",
                            "user_english_name": j.student_id.english_name if j.student_id else "",
                            "student_id": j.student_id.student_id if j.student_id else "",
                            "class_no": j.student_id.class_no if j.student_id else "",
                            "class_id": j.student_id.class_id.id if j.student_id.class_id else "",
                            "class_name": j.student_id.class_id.class_name if j.student_id.class_id else "",
                            "student_contact_no": j.applicant_service_id.student_contact_no if j.applicant_service_id.student_contact_no else "",
                            "parent_contact_no": j.applicant_service_id.parent_contact_no if j.applicant_service_id.parent_contact_no else "",
                            "parent_consent": j.applicant_service_id.parent_consent if j.applicant_service_id.parent_consent else False,
                            "date_of_application": j.applicant_service_id.date_of_application if j.applicant_service_id.date_of_application else "",
                            "approval_status": j.approval_status if j.approval_status else "",
                            "created_date": str(j.created_date),
                            "reminder": j.reminder if j.reminder else "",
                            "object": "Mission disapproval",
                            "notification_opened_status": j.notification_opened_status if j.notification_opened_status else False,
                            "disapproval_date": str(
                                j.applicant_service_id.disapproval_date + timedelta(hours=8)) if j.applicant_service_id.disapproval_date else "",
                        }
                        records.append(service_val)
                        if j.notification_opened_status is False:
                            count = count + 1
                else:
                    return Response({"success": False, "message": "Not Found", "data": {}},
                                    status=status.HTTP_400_BAD_REQUEST)
            service_records = {
                "record_count": len(records),
                "unopened_notifications": count,
                "records": sorted(records, key=lambda x: x['created_date'], reverse=True),
            }
            return Response({
                "success": True,
                "message": "Success",
                "data": service_records,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class ImportRecord(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AddStudentCreateSerializer

    def post(self, request, *args, **kwargs):
        data = request.data.get('data')
        lis = []
        form_names = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6']
        class_names = ['1H', '1K', '1W', '1Y', '2H', '2K', '2W', '2Y', '3H', '3K', '3W', '3Y',
                       '4H', '4K', '4W', '4Y', '5H', '5K', '5W', '5Y', '6H', '6K', '6W', '6Y']
        email_list = [x.email for x in User.objects.all()]
        student_id_list = [y.student_id for y in User.objects.all()]
        for i in data:
            if i.get('email') in email_list:
                return Response({"success": False, "message": " The email id already exist"},
                                status=status.HTTP_400_BAD_REQUEST)
            if i.get('student_id') in student_id_list:
                return Response({"success": False, "message": " The student id already exist"},
                                status=status.HTTP_400_BAD_REQUEST)
            if i.get('form_id') not in form_names:
                return Response({"success": False, "message": "The form is in_correct"}, status=status.HTTP_400_BAD_REQUEST)
            if i.get('class_id') not in class_names:
                return Response({"success": False, "message": "The class is in_correct"}, status=status.HTTP_400_BAD_REQUEST)
            if i.get('form_id') in form_names and i.get('class_id') in class_names and i.get('gender') in ['M', 'F']:

                new_user = User.objects.create(user_id=i.get('email'),
                                               student_id=i.get('student_id'),
                                               email=i.get('email'),
                                               english_name=i.get('english_name'),
                                               chinese_name=i.get('chinese_name'),
                                               class_no=i.get('class_no'),
                                               class_id=Class.objects.get(class_name=i.get('class_id')),
                                               form_id=Form.objects.get(form_name=i.get('form_id')),
                                               gender='Male' if i.get('gender') == 'M' else 'Female',
                                               # birth_date=i.get('birth_date'),
                                               birth_date=datetime.strptime(i.get('birth_date'), '%d-%m-%Y').strftime('%Y-%m-%d'),
                                               year_of_joining=i.get('year_of_joining'),
                                               is_student=True)
                serializer = AddStudentCreateSerializer(new_user)
                lis.append(serializer.data)
        return Response({
            "success": True,
            "message": "Success",
            "data": lis
        }, status=status.HTTP_201_CREATED)


class ReportFilter(generics.ListCreateAPIView):
    """
        Get Student Service List
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ServicesSerializer
    queryset = ServiceRecords.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Get all Service Records Filter
            :param request: Service Records
            :param kwargs: NA
            :return: Service Records
        """

        start = request.data.get('start_date')
        start_date = datetime.strptime(start, '%d/%m/%Y').strftime('%Y-%m-%d')
        end = request.data.get('end_date')
        end_date = datetime.strptime(end, '%d/%m/%Y').strftime('%Y-%m-%d')

        paginator = ServiceRecordsPagination()
        page_size = paginator.page_size

        snippets = ServiceRecords.objects.filter(user_id__is_student=True,
                                                 created_date__date__gte=start_date,
                                                 created_date__date__lte=end_date)
        print(snippets)
        service_records = []
        seq = 1
        if snippets:
            for i in snippets:
                school_service = ServiceRecords.objects.filter(user_id=i.user_id, service_type="school")
                home_service = ServiceRecords.objects.filter(user_id=i.user_id, service_type="home")
                community_service = ServiceRecords.objects.filter(user_id=i.user_id, service_type="community")
                school_service_hrs = 0
                home_service_hrs = 0
                community_service_hrs = 0
                if school_service:
                    for x in school_service:
                        if x.service_duration:
                            formatted_time = dt.strptime(x.service_duration, '%H:%M:%S.%f').time()
                            hour_school = formatted_time.hour
                            minute_school = formatted_time.minute
                            school_time = hour_school * 60 + minute_school
                            total_hrs = 0
                            if school_time > 0:
                                total_hrs = school_time / 60
                            school_service_hrs = round(school_service_hrs + total_hrs, 2)
                if home_service:
                    for x in home_service:
                        if x.service_duration:
                            formatted_time = dt.strptime(x.service_duration, '%H:%M:%S.%f').time()
                            hour_school = formatted_time.hour
                            minute_school = formatted_time.minute
                            school_time = hour_school * 60 + minute_school
                            total_hrs = 0
                            if school_time > 0:
                                total_hrs = school_time / 60
                            home_service_hrs = home_service_hrs + total_hrs
                if community_service:
                    for x in community_service:
                        if x.service_duration:
                            formatted_time = dt.strptime(x.service_duration, '%H:%M:%S.%f').time()
                            hour_school = formatted_time.hour
                            minute_school = formatted_time.minute
                            school_time = hour_school * 60 + minute_school
                            total_hrs = 0
                            if school_time > 0:
                                total_hrs = school_time / 60
                            community_service_hrs = community_service_hrs + total_hrs

                total_school = school_service_hrs
                total_community_home = home_service_hrs + community_service_hrs
                total_community_home_school = home_service_hrs + community_service_hrs + school_service_hrs

                total_school_hours = int(total_school)
                total_school_minutes = int((total_school * 60) % 60)
                total_school_val = str(total_school_hours) + ":" + str(total_school_minutes)

                total_community_home_hours = int(total_community_home)
                total_community_home_minutes = int((total_community_home * 60) % 60)
                total_community_home_val = str(total_community_home_hours) + ":" + str(total_community_home_minutes)

                total_community_home_school_hours = int(total_community_home_school)
                total_community_home_school_minutes = int((total_community_home_school * 60) % 60)
                total_community_home_school_val = str(total_community_home_school_hours) + ":" + str(
                    total_community_home_school_minutes)

                if total_school == 0:
                    total_school_val = "0"
                if total_community_home == 0:
                    total_community_home_val = "0"
                if total_community_home_school == 0:
                    total_community_home_school_val = "0"

                service_vals = {
                    "id": i.id if i.id else False,
                    "sequence": seq,
                    "user_id": i.user_id.id if i.user_id.id else "",
                    "class_no": i.user_id.class_no if i.user_id.class_no else "",
                    "user_name": i.user_id.user_id if i.user_id.user_id else "",
                    "user_english_name": i.user_id.english_name if i.user_id.english_name else "",
                    "user_chinese_name": i.user_id.chinese_name if i.user_id.chinese_name else "",
                    "student_id": i.user_id.student_id if i.user_id.student_id else "",
                    "email": i.user_id.email if i.user_id.email else "",
                    "serving_date": i.serving_date if i.serving_date else "",
                    "serving_from_date_time": i.serving_from_date_time if i.serving_from_date_time else "",
                    "serving_to_date_time": i.serving_to_date_time if i.serving_to_date_time else "",
                    "service_duration": i.service_duration if i.service_duration else "",
                    "approval_status": i.approval_status if i.approval_status else "",
                    "home_and_community_service": total_community_home_val if total_community_home_val else "0",
                    "school_service": total_school_val if total_school_val else "0",
                    "total_service_hr_this_year": total_community_home_school_val if total_community_home_school_val else "0",
                    "created_date": str(i.created_date),
                    "updated_date": str(i.updated_date),

                }
                service_records.append(service_vals)
                seq = seq + 1
            sorted_service_records = sorted(service_records, key=lambda x: x['sequence'], reverse=True)

            result_page = paginator.paginate_queryset(sorted_service_records, request)
            paginator_data = paginator.get_paginated_response(result_page).data
            if len(sorted_service_records) > 0:
                paginator_data['total_pages'] = math.ceil(len(sorted_service_records) / page_size)
            else:
                return Response({"success": False, "message": "No data"},
                                status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "success": True,
                "message": "Success",
                "data": paginator_data,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


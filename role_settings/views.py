from rest_framework import status, generics
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.response import Response
from .serializers import RoleSettingSerializer
from .models import RoleSetting
from accounts.models import User
from rest_framework.permissions import IsAuthenticated
from .pagination import RoleSettingsPagination
import math
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404


class RoleSettingsAPI(generics.ListCreateAPIView):
    """
        List and Create Role Settings
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = RoleSettingSerializer
    queryset = RoleSetting.objects.all().order_by('id')

    def get_object(self, pk):
        """
        Fetch corresponding snippets object
        :param pk: snippets id
        :return: snippets object
        """
        try:
            return self.queryset.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_user(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        """
            create Roles
            :param request: Role Settings
            :param kwargs: NA
            :return: Role Settings details
        """
        if not request.user.student_id:
            if request.user.role_id is None:
                return Response({"success": False, "message": "User has no role id set"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not (request.user.role_id.all_privileges or request.user.role_id.add_role):
                return Response({"success": False, "message": "User has no privilege to add role"},
                                status=status.HTTP_400_BAD_REQUEST)
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
        :param kwargs: Role id
        :return: message
        """
        if not request.user.student_id:
            if request.user.role_id is None:
                return Response({"success": False, "message": "User has no role id set"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not (request.user.role_id.all_privileges or request.user.role_id.delete_role):
                return Response({"success": False, "message": "User has no privilege to delete role"},
                                status=status.HTTP_400_BAD_REQUEST)
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
        if not request.user.student_id:
            if request.user.role_id is None:
                return Response({"success": False, "message": "User has no role id set"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not (request.user.role_id.all_privileges or request.user.role_id.edit_role):
                return Response({"success": False, "message": "User has no privilege to edit role"},
                                status=status.HTTP_400_BAD_REQUEST)
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


class RoleSettingsList(generics.ListCreateAPIView):
    """
        Get Role Settings List
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = RoleSettingSerializer
    queryset = RoleSetting.objects.all().order_by('id')

    def post(self, request, *args, **kwargs):
        """
            Get all Role Settings
            :param request: Service Records
            :param kwargs: NA
            :return: all Role Settings
        """

        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        paginator = RoleSettingsPagination()
        page_size = paginator.page_size

        snippets = self.queryset.all()
        role_records = []
        seq = 1
        if snippets:
            for i in snippets:
                role_vals = {
                    "id": i.id if i.id else False,
                    "role_title": i.role_title if i.role_title else "",
                    "level": i.level if i.level else "",
                    "all_privileges": i.all_privileges,
                    "records_approval": i.records_approval,
                    "records_approval_home": i.records_approval_home,
                    "records_approval_school": i.records_approval_school,
                    "records_approval_community": i.records_approval_community,
                    "post_services": i.post_services,
                    "post_services_teachers_sharing": i.post_services_teachers_sharing,
                    "post_services_school": i.post_services_school,
                    "post_services_community": i.post_services_community,
                    "monitoring": i.monitoring,
                    "monitoring_chat_room": i.monitoring_chat_room,
                    "monitoring_home_service": i.monitoring_home_service,
                    "monitoring_share_record_area": i.monitoring_share_record_area,
                    "service_record": i.service_record,
                    "service_record_import": i.service_record_import,
                    "service_record_export_full_list": i.service_record_export_full_list,
                    "service_record_export_individual_record": i.service_record_export_individual_record,
                    "service_record_add_student": i.service_record_add_student,
                    "redeemed_items": i.redeemed_items,
                    "redeem_item_list": i.redeem_item_list,
                    "redeem_item_record": i.redeem_item_record,
                    "role_setting": i.role_setting,
                    "add_role": i.add_role,
                    "edit_role": i.edit_role,
                    "delete_role": i.delete_role,
                    "is_active": i.is_active,
                    "created_date": str(i.created_date),
                    "updated_date": str(i.updated_date)
                }
                role_records.append(role_vals)
                seq = seq + 1

            result_page = paginator.paginate_queryset(role_records, request)
            paginator_data = paginator.get_paginated_response(result_page).data
            if len(role_records) > 0:
                paginator_data['total_pages'] = math.ceil(len(role_records) / page_size)
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


class RoleSettingsForm(generics.ListCreateAPIView):
    """
        Get Single Service Record
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = RoleSettingSerializer
    queryset = RoleSetting.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Get Role Settings Record
            :param request: Service Record id
            :param kwargs: NA
            :return: Specific Role Settings Record
        """
        role_id = request.data.get('id')
        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        if role_id:
            snippets = self.queryset.filter(id=role_id)
            if snippets:
                for i in snippets:
                    role_vals = {
                        "id": i.id if i.id else False,
                        "role_title": i.role_title if i.role_title else "",
                        "level": i.level if i.level else "",
                        "all_privileges": i.all_privileges,
                        "records_approval": i.records_approval,
                        "records_approval_home": i.records_approval_home,
                        "records_approval_school": i.records_approval_school,
                        "records_approval_community": i.records_approval_community,
                        "post_services": i.post_services,
                        "post_services_teachers_sharing": i.post_services_teachers_sharing,
                        "post_services_school": i.post_services_school,
                        "post_services_community": i.post_services_community,
                        "monitoring": i.monitoring,
                        "monitoring_chat_room": i.monitoring_chat_room,
                        "monitoring_home_service": i.monitoring_home_service,
                        "monitoring_share_record_area": i.monitoring_share_record_area,
                        "service_record": i.service_record,
                        "service_record_import": i.service_record_import,
                        "service_record_export_full_list": i.service_record_export_full_list,
                        "service_record_export_individual_record": i.service_record_export_individual_record,
                        "service_record_add_student": i.service_record_add_student,
                        "redeemed_items": i.redeemed_items,
                        "redeem_item_list": i.redeem_item_list,
                        "redeem_item_record": i.redeem_item_record,
                        "role_setting": i.role_setting,
                        "add_role": i.add_role,
                        "edit_role": i.edit_role,
                        "delete_role": i.delete_role,
                        "is_active": i.is_active,
                        "created_date": str(i.created_date),
                        "updated_date": str(i.updated_date)
                    }
                    return Response({
                        "success": True,
                        "message": "Success",
                        "data": role_vals,
                    }, status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "Not Found", "data": {}},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


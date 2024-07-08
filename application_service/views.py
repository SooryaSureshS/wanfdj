from rest_framework import status, generics
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.response import Response
from .serializers import ApplicationServiceSerializer, TeachersSharingSerializer, \
    ApplicationServiceApplicantsSerializer, NotificationSerializer
from .models import ApplicationService, TeachersSharing, ApplicationServiceApplicants, Notification
from accounts.models import User, Class, Form
from rest_framework.permissions import IsAuthenticated
from .pagination import ApplicationForServicePagination
import math
import pytz
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from datetime import datetime, timedelta, time


class ApplicationServices(generics.ListCreateAPIView):
    """
        List and Create Application Services
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = ApplicationServiceSerializer
    queryset = ApplicationService.objects.all().order_by('id')

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
            create Application Services
            :param request: Application Services
            :param kwargs: NA
            :return: Application Services details
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


class ApplicationServicesFilter(generics.ListCreateAPIView):
    """
        Get Student Service List
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ApplicationServiceSerializer
    queryset = ApplicationService.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Get all Service Records Filter
            :param request: Service Records
            :param kwargs: NA
            :return: Service Records
        """
        service_type = request.data.get('service_type')

        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        paginator = ApplicationForServicePagination()
        page_size = paginator.page_size

        if service_type:
            snippets = self.queryset.filter(service_type=service_type).order_by('id')
        else:
            snippets = self.queryset.all()
        service_records = []
        seq = 1
        if snippets:
            for i in snippets:
                service_vals = {
                    "id": i.id if i.id else False,
                    "sequence": seq,
                    "teacher_name": i.teacher_name if i.teacher_name else False,
                    "no_of_students": i.no_of_students if i.no_of_students else False,
                    "service_type": i.service_type if i.service_type else False,
                    "service_date": i.service_date if i.service_date else False,
                    "serving_from_time": i.serving_from_time if i.serving_from_time else False,
                    "serving_to_time": i.serving_to_time if i.serving_to_time else False,
                    "service_description": i.service_description if i.service_description else "",
                    "publish_date": i.publish_date if i.publish_date else False,
                    "publish_time": i.publish_time if i.publish_time else False,
                    "location": i.location if i.location else False,
                    "attachment": urls + "/application/service/media/" + str(
                        i.attachment) if i.attachment else False,
                    "status": i.status if i.status else False,
                    "created_date": str(i.created_date),
                    "updated_date": str(i.updated_date),
                    "service_deadline_date": i.service_deadline_date if i.service_deadline_date else "",
                    "service_deadline_time": i.service_deadline_time if i.service_deadline_time else ""
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


class ApplicationServicesForm(generics.ListCreateAPIView):
    """
        Get Student Service List
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ApplicationServiceSerializer
    queryset = ApplicationService.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Get all Service Records Filter
            :param request: Service Records
            :param kwargs: NA
            :return: Service Records
        """
        service_id = request.data.get('id')

        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        snippets = self.queryset.filter(id=service_id).first()

        if snippets:
            i = snippets
            applicants = ApplicationServiceApplicants.objects.filter(application_service_id=i.id).order_by('-id')
            service_records_applicants = []
            if applicants:
                for k in applicants:
                    applicants_dict = {
                        "id": k.id if k.id else False,
                        "student_id": k.student_id.id if k.student_id.id else False,
                        "student_name": k.student_id.english_name if k.student_id.english_name else False,
                        "class_no": k.class_no if k.class_no else "",
                        "class_id": k.class_id.id if k.class_id else "",
                        "class_name": k.class_id.class_name if k.class_id else "",
                        "student_contact_no": k.student_contact_no if k.student_contact_no else False,
                        "parent_contact_no": k.parent_contact_no if k.parent_contact_no else False,
                        "parent_consent": k.parent_consent if k.parent_consent else False,
                        "date_of_application": k.date_of_application if k.date_of_application else False,
                        "status": k.status if k.status else False,
                        "created_date": str(k.created_date),
                        "updated_date": str(k.updated_date)
                    }
                    service_records_applicants.append(applicants_dict)
            service_vals = {
                "id": i.id if i.id else False,
                "teacher_name": i.teacher_name if i.teacher_name else False,
                "no_of_students": i.no_of_students if i.no_of_students else False,
                "service_type": i.service_type if i.service_type else False,
                "service_date": i.service_date if i.service_date else False,
                "serving_from_time": i.serving_from_time if i.serving_from_time else False,
                "serving_to_time": i.serving_to_time if i.serving_to_time else False,
                "service_description": i.service_description if i.service_description else "",
                "publish_date": i.publish_date if i.publish_date else False,
                "publish_time": i.publish_time if i.publish_time else False,
                "location": i.location if i.location else False,
                "attachment": urls + "/application/service/media/" + str(
                    i.attachment) if i.attachment else False,
                "status": i.status if i.status else False,
                "created_date": str(i.created_date),
                "updated_date": str(i.updated_date),
                "applicants": service_records_applicants,
                "service_deadline_date": i.service_deadline_date if i.service_deadline_date else "",
                "service_deadline_time": i.service_deadline_time if i.service_deadline_time else ""
            }
            return Response({
                "success": True,
                "message": "Success",
                "data": service_vals,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class ApplicationServicesNotification(generics.ListCreateAPIView):
    """
            Get Student Service List
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ApplicationServiceApplicantsSerializer
    queryset = ApplicationServiceApplicants.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Applicant Details Update
            :param request: applicant_record_id
            :param kwargs: NA
            :return: Update status
        """
        student_id = request.data.get('student_id')
        application_service_applicant_id = request.data.get('application_service_applicant_id')
        reminder = request.data.get('reminder')
        student_obj = User.objects.get(id=student_id)
        application_service_applicant_obj = ApplicationServiceApplicants.objects.get(id=application_service_applicant_id)

        noti_obj = Notification(student_id_id=student_obj.id,
                                applicant_service_id_id=application_service_applicant_obj.id,
                                service_id=application_service_applicant_obj.application_service_id,
                                reminder=reminder,
                                approval_status=application_service_applicant_obj.status)
        noti_obj.save()
        serializer = NotificationSerializer(noti_obj)
        return Response({
            "success": True,
            "message": "Success",
            "data": serializer.data,
        }, status=status.HTTP_200_OK)


class MissionForm(generics.ListCreateAPIView):
    """
        Get Single Service Record
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        application_service_id = request.data.get('id')
        if application_service_id:
            snippets = self.queryset.filter(id=application_service_id)
            if snippets:
                for i in snippets:
                    if i.student_id or i.applicant_service_id:

                        service_vals = {
                            "id": i.id,
                            "user_id": i.student_id.id if i.student_id else "",
                            "user_name": i.student_id.student_id if i.student_id else "",
                            "user_english_name": i.student_id.english_name if i.student_id else "",
                            "student_id": i.student_id.student_id if i.student_id else "",
                            "class_no": i.student_id.class_no if i.student_id else "",
                            "class_id": i.student_id.class_id.id if i.student_id.class_id else "",
                            "class_name": i.student_id.class_id.class_name if i.student_id.class_id else "",
                            "student_contact_no": i.applicant_service_id.student_contact_no if i.applicant_service_id.student_contact_no else "",
                            "parent_contact_no": i.applicant_service_id.parent_contact_no if i.applicant_service_id.parent_contact_no else "",
                            "parent_consent": i.applicant_service_id.parent_consent if i.applicant_service_id.parent_consent else False,
                            "date_of_application": i.applicant_service_id.date_of_application if i.applicant_service_id.date_of_application else "",
                            "approval_status": i.approval_status if i.approval_status else "",
                            "created_date": str(i.created_date),
                            "updated_date": str(i.applicant_service_id.updated_date),
                            "reminder": i.reminder if i.reminder else "",
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


class ApplicantUpdate(generics.ListCreateAPIView):
    """
        Service Record Status Update
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = ApplicationServiceApplicantsSerializer
    queryset = ApplicationServiceApplicants.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Applicant Details Update
            :param request: applicant_record_id
            :param kwargs: NA
            :return: Update status
        """

        applicant_record_id = request.data.get('id')
        application_status = request.data.get('status')
        parent_consent = request.data.get('parent_consent')

        if applicant_record_id:
            data = ApplicationServiceApplicants.objects.get(id=applicant_record_id)
            if data:
                if application_status:
                    data.status = application_status
                if parent_consent:
                    data.parent_consent = parent_consent
                if application_status == "disapproved":
                    data.disapproval_date = datetime.now()
                if application_status == "approved":
                    data.approval_date = datetime.now()
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


class TeachersSharingAPI(generics.ListCreateAPIView):
    """
        List and Create Teachers Sharing
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = TeachersSharingSerializer
    queryset = TeachersSharing.objects.all().order_by('id')

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
            create Teacher Sharing details
            :param request: Teacher Sharing details
            :param kwargs: NA
            :return: Teacher Sharing details
        """
        if not request.user.student_id:
            if request.user.role_id is None:
                return Response({"success": False, "message": "User has no role id set"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not (request.user.role_id.all_privileges or (
                    request.user.role_id.post_services and request.user.role_id.post_services_teachers_sharing)):
                return Response({"success": False, "message": "User has no privilege"},
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
        :param kwargs: snippets id
        :return: message
        """
        if not request.user.student_id:
            if request.user.role_id is None:
                return Response({"success": False, "message": "User has no role id set"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not (request.user.role_id.all_privileges or (
                    request.user.role_id.post_services and request.user.role_id.post_services_teachers_sharing)):
                return Response({"success": False, "message": "User has no privilege"},
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
            if not (request.user.role_id.all_privileges or (
                    request.user.role_id.post_services and request.user.role_id.post_services_teachers_sharing)):
                return Response({"success": False, "message": "User has no privilege"},
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


class TeachersSharingForm(generics.ListCreateAPIView):
    """
        Teacher Sharing Form
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = TeachersSharingSerializer
    queryset = TeachersSharing.objects.all().order_by('id')

    def post(self, request, *args, **kwargs):
        """
            Get all Service Records Filter
            :param request: Service Records
            :param kwargs: NA
            :return: Service Records
        """
        if not request.user.student_id:
            if request.user.role_id is None:
                return Response({"success": False, "message": "User has no role id set"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not (request.user.role_id.all_privileges or (
                    request.user.role_id.post_services or request.user.role_id.post_services_teachers_sharing)):
                return Response({"success": False, "message": "User has no privilege"},
                                status=status.HTTP_400_BAD_REQUEST)

        teacher_sharing_id = request.data.get('id')
        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        snippets = self.queryset.filter(id=teacher_sharing_id).first()

        if snippets:
            i = snippets
            service_vals = {
                "id": i.id if i.id else False,
                "teacher_name": i.teacher_name if i.teacher_name else False,
                "title": i.title if i.title else False,
                "content": i.content if i.content else False,
                "service_date": i.service_date if i.service_date else False,
                "attachment": urls + "/application/service/media/" + str(
                    i.attachment) if i.attachment else False,
                "status": i.status if i.status else False,
                "created_date": str(i.created_date),
                "updated_date": str(i.updated_date)
            }
            return Response({
                "success": True,
                "message": "Success",
                "data": service_vals,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class TeachersSharingList(generics.ListCreateAPIView):
    """
        Teacher Sharing List
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = TeachersSharingSerializer
    queryset = TeachersSharing.objects.all().order_by('id')

    def post(self, request, *args, **kwargs):
        """
            Get all Teacher Service Records List
            :param request: Teacher Service Records
            :param kwargs: NA
            :return: Teacher Service Records
        """
        if not request.user.student_id:
            if request.user.role_id is None:
                return Response({"success": False, "message": "User has no role id set"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not (
                    request.user.role_id.all_privileges or request.user.role_id.post_services or request.user.role_id.post_services_teachers_sharing):
                return Response({"success": False, "message": "User has no privilege"},
                                status=status.HTTP_400_BAD_REQUEST)

        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        paginator = ApplicationForServicePagination()
        page_size = paginator.page_size

        snippets = self.queryset.all()
        service_data = []
        seq = 1
        if snippets:
            for i in snippets:
                service_vals = {
                    "id": i.id if i.id else False,
                    "sequence": seq,
                    "teacher_name": i.teacher_name if i.teacher_name else False,
                    "title": i.title if i.title else False,
                    "content": i.content if i.content else False,
                    "service_date": i.service_date if i.service_date else False,
                    "attachment": urls + "/application/service/media/" + str(
                        i.attachment) if i.attachment else False,
                    "status": i.status if i.status else False,
                    "created_date": str(i.created_date),
                    "updated_date": str(i.updated_date)
                }
                service_data.append(service_vals)
                seq = seq + 1
            sorted_service_data = sorted(service_data, key=lambda x: x['sequence'], reverse=True)

            result_page = paginator.paginate_queryset(sorted_service_data, request)
            paginator_data = paginator.get_paginated_response(result_page).data
            if len(sorted_service_data) > 0:
                paginator_data['total_pages'] = math.ceil(len(sorted_service_data) / page_size)
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


class ActiveTeachersSharingList(generics.ListCreateAPIView):
    """
        Teacher Sharing List
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = TeachersSharingSerializer
    queryset = TeachersSharing.objects.all().order_by('id')

    def post(self, request, *args, **kwargs):
        """
            Get all Teacher Service Records List
            :param request: Teacher Service Records
            :param kwargs: NA
            :return: Teacher Service Records
        """

        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        snippets = self.queryset.filter(status=True)
        service_data = []
        if snippets:
            for i in snippets:
                service_vals = {
                    "id": i.id if i.id else "",
                    "teacher_name": i.teacher_name if i.teacher_name else "",
                    "title": i.title if i.title else "",
                    "content": i.content if i.content else "",
                    "service_date": i.service_date if i.service_date else "",
                    "attachment": urls + "/application/service/media/" + str(
                        i.attachment) if i.attachment else "",
                    "status": i.status if i.status else "",
                    "created_date": str(i.created_date),
                    "updated_date": str(i.updated_date)
                }
                service_data.append(service_vals)

            return Response({
                "success": True,
                "message": "Success",
                "data": service_data,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class MissionAreaList(generics.ListCreateAPIView):
    """
        Teacher Sharing List
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ApplicationServiceSerializer
    queryset = ApplicationService.objects.all().order_by('id')

    def post(self, request, *args, **kwargs):
        """
            Get Application for service
            :param request: Application for service
            :param kwargs: NA
            :return: Application for service
        """

        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        hkt = pytz.timezone('Asia/Hong_Kong')
        current_date = datetime.now(hkt)
        current_time = str(current_date)
        snippets = self.queryset.filter(status=True)
        service_records = []
        if snippets:
            for i in snippets:
                if i.service_deadline_date is not None and i.service_deadline_time is not None:
                    dt_obj = f"{str(i.service_deadline_date)} {str(i.service_deadline_time)}"
                    date_obj = datetime.strptime(str(dt_obj), '%Y-%m-%d %H:%M:%S') + timedelta(hours=2, minutes=30)
                    if str(date_obj) <= current_time:
                        if i.status is True:
                            i.status = False
                            i.save()
                    if str(date_obj) >= current_time:
                        service_vals = {
                            "id": i.id if i.id else "",
                            "teacher_name": i.teacher_name if i.teacher_name else "",
                            "no_of_students": i.no_of_students if i.no_of_students else "",
                            "service_type": i.service_type if i.service_type else "",
                            "service_date": i.service_date if i.service_date else "",
                            "serving_from_time": i.serving_from_time if i.serving_from_time else "",
                            "serving_to_time": i.serving_to_time if i.serving_to_time else "",
                            "service_description": i.service_description if i.service_description else "",
                            "publish_date": i.publish_date if i.publish_date else "",
                            "publish_time": i.publish_time if i.publish_time else "",
                            "location": i.location if i.location else "",
                            "attachment": urls + "/application/service/media/" + str(
                                i.attachment) if i.attachment else "",
                            "status": i.status if i.status else False,
                            "created_date": str(i.created_date),
                            "updated_date": str(i.updated_date),
                            "service_deadline_date": i.service_deadline_date if i.service_deadline_date else "",
                            "service_deadline_time": i.service_deadline_time if i.service_deadline_time else ""
                        }
                        service_records.append(service_vals)

            return Response({
                "success": True,
                "message": "Success",
                "data": service_records,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class MissionAreaForm(generics.ListCreateAPIView):
    """
        Get Student Service List
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ApplicationServiceSerializer
    queryset = ApplicationService.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Get all Service Records Filter
            :param request: Service Records
            :param kwargs: NA
            :return: Service Records
        """
        service_id = request.data.get('id')
        user_id = request.data.get('user_id')

        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        snippets = self.queryset.filter(id=service_id).first()

        if snippets:
            i = snippets
            applicants = ApplicationServiceApplicants.objects.filter(application_service_id=i.id,
                                                                     student_id=user_id).order_by('-id')
            already_applied = False
            if applicants:
                already_applied = True
            service_vals = {
                "id": i.id if i.id else "",
                "teacher_name": i.teacher_name if i.teacher_name else "",
                "no_of_students": i.no_of_students if i.no_of_students else "",
                "service_type": i.service_type if i.service_type else "",
                "service_date": i.service_date if i.service_date else "",
                "serving_from_time": i.serving_from_time if i.serving_from_time else "",
                "serving_to_time": i.serving_to_time if i.serving_to_time else "",
                "service_description": i.service_description if i.service_description else "",
                "publish_date": i.publish_date if i.publish_date else "",
                "publish_time": i.publish_time if i.publish_time else "",
                "location": i.location if i.location else "",
                "attachment": urls + "/application/service/media/" + str(
                    i.attachment) if i.attachment else "",
                "status": i.status if i.status else False,
                "created_date": str(i.created_date),
                "updated_date": str(i.updated_date),
                "service_deadline_date": i.service_deadline_date if i.service_deadline_date else "",
                "service_deadline_time": i.service_deadline_time if i.service_deadline_time else "",
                "already_applied": already_applied
            }
            return Response({
                "success": True,
                "message": "Success",
                "data": service_vals,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class MissionAreaAccept(generics.ListCreateAPIView):
    """
        List and Create Application Services
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = ApplicationServiceApplicantsSerializer
    queryset = ApplicationServiceApplicants.objects.all().order_by('id')

    def post(self, request, *args, **kwargs):
        """
            Create Applicant Services
            :param request: Applicant Services
            :param kwargs: NA
            :return: Applicant Services details
        """
        try:
            user_id = request.data.get('student_id')
            application_service_id = request.data.get('application_service_id')
            user_data = User.objects.filter(id=user_id).first()
            application_service_data = ApplicationService.objects.filter(id=application_service_id).first()
            if user_data and application_service_data:
                class_data = False
                if user_data.class_id:
                    class_data = Class.objects.filter(id=user_data.class_id.id).first()
                if not class_data:
                    class_data = False

                applicant_data = ApplicationServiceApplicants.objects.create(student_id=user_data,
                                                                             application_service_id=application_service_data,
                                                                             student_name=user_data.english_name if user_data.english_name else "",
                                                                             class_no=user_data.class_no if user_data.class_no else "",
                                                                             parent_contact_no=user_data.parent_phone_no if user_data.parent_phone_no else "",
                                                                             student_contact_no=user_data.student_phone_no if user_data.student_phone_no else "",
                                                                             class_id=class_data if class_data else None
                                                                             )
                return Response({
                    "success": True,
                    "message": "Success",
                }, status=status.HTTP_201_CREATED)

            else:

                return Response({
                    "success": False,
                    "message": "Not Found",
                }, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"success": False, "message": "Failed", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        """
        snippets delete
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
        Applicant Services Edit
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


class MissionAreaAcceptUpdate(generics.ListCreateAPIView):
    """
        Mission Area Accept Update
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all().order_by('id')

    def get_object(self, pk):
        try:
            return self.queryset.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404

    def get_user(self):
        return self.request.user

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


class MyMissionList(generics.ListCreateAPIView):
    """
        Teacher Sharing List
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all().order_by('id')

    def post(self, request, *args, **kwargs):
        """
            Get Application for service
            :param request: Application for service
            :param kwargs: NA
            :return: Application for service
        """
        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)
        user_id = request.data.get('user_id')

        user = User.objects.get(id=user_id)
        snippets = Notification.objects.filter(student_id=user)
        service_records = []
        if snippets:
            for i in snippets:
                service_vals = {
                    "id": i.id if i.id else "",
                    "application_service_id": i.service_id.id if i.service_id.id else "",
                    "student_id": i.student_id.id if i.student_id.id else "",
                    "student_english_name": i.student_id.english_name if i.student_id.english_name else "",
                    "student_chinese_namee": i.student_id.chinese_name if i.student_id.chinese_name else "",
                    "teacher_name": i.service_id.teacher_name if i.service_id.teacher_name else "",
                    "no_of_students": i.service_id.no_of_students if i.service_id.no_of_students else "",
                    "service_type": i.service_id.service_type if i.service_id.service_type else "",
                    "service_date": i.service_id.service_date if i.service_id.service_date else "",
                    "serving_from_time": i.service_id.serving_from_time if i.service_id.serving_from_time else "",
                    "serving_to_time": i.service_id.serving_to_time if i.service_id.serving_to_time else "",
                    "service_description": i.service_id.service_description if i.service_id.service_description else "",
                    "publish_date": i.service_id.publish_date if i.service_id.publish_date else "",
                    "publish_time": i.service_id.publish_time if i.service_id.publish_time else "",
                    "location": i.service_id.location if i.service_id.location else "",
                    "attachment": urls + "/application/service/media/" + str(
                        i.service_id.attachment) if i.service_id.attachment else "",
                    "approval_status": i.approval_status if i.approval_status else False,
                    "created_date": str(i.created_date),

                }
                service_records.append(service_vals)

            return Response({
                "success": True,
                "message": "Success",
                "data": service_records,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class MyMissionForm(generics.ListCreateAPIView):
    """
        Teacher Sharing List
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all().order_by('id')

    def post(self, request, *args, **kwargs):
        """
            Get Application for service
            :param request: Application for service
            :param kwargs: NA
            :return: Application for service
        """

        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)
        pk = request.data.get('id')
        print(pk)
        snippets = Notification.objects.filter(id=pk)
        print(snippets)
        service_records = []
        if snippets:
            for i in snippets:
                service_vals = {

                    "id": i.id if i.id else "",
                    "application_service_id": i.service_id.id if i.service_id.id else "",
                    "student_id": i.student_id.id if i.student_id.id else "",
                    "student_english_name": i.student_id.english_name if i.student_id.english_name else "",
                    "student_chinese_namee": i.student_id.chinese_name if i.student_id.chinese_name else "",
                    "teacher_name": i.service_id.teacher_name if i.service_id.teacher_name else "",
                    "no_of_students": i.service_id.no_of_students if i.service_id.no_of_students else "",
                    "service_type": i.service_id.service_type if i.service_id.service_type else "",
                    "service_date": i.service_id.service_date if i.service_id.service_date else "",
                    "serving_from_time": i.service_id.serving_from_time if i.service_id.serving_from_time else "",
                    "serving_to_time": i.service_id.serving_to_time if i.service_id.serving_to_time else "",
                    "service_description": i.service_id.service_description if i.service_id.service_description else "",
                    "publish_date": i.service_id.publish_date if i.service_id.publish_date else "",
                    "publish_time": i.service_id.publish_time if i.service_id.publish_time else "",
                    "location": i.service_id.location if i.service_id.location else "",
                    "attachment": urls + "/application/service/media/" + str(
                        i.service_id.attachment) if i.service_id.attachment else "",
                    "approval_status": i.approval_status if i.approval_status else False,
                    "created_date": str(i.created_date),
                    "reminder": i.reminder if i.reminder else "",

                }
                service_records.append(service_vals)

                return Response({
                    "success": True,
                    "message": "Success",
                    "data": service_vals,
                }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


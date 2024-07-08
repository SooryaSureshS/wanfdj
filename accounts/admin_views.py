import random
import uuid
from knox.models import AuthToken
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.conf import settings
from accounts.models import User, Form, Class
from role_settings.models import RoleSetting
from .serializers import UserSerializer, TokenSerializer, AdminLoginSerializer, AdminRegisterSerializer
from .serializers import FormSerializer, ClassSerializer
from django.core.mail import send_mail
from rest_framework.permissions import IsAuthenticated
from .pagination import AccountsPagination
import math


class UserCreateAPI(generics.GenericAPIView):
    serializer_class = AdminRegisterSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = AdminRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "success": True,
                "message": "Account Created",
                "data":
                    {
                        "user": AdminRegisterSerializer(user, context=self.get_serializer_context()).data,
                        "user_password": request.data.get('password'),
                        "token": AuthToken.objects.create(user)[1]
                    },
            }, status=status.HTTP_200_OK)
        else:
            email = request.data.get('email')
            email_exist = User.objects.filter(email=email).exists()
            if email_exist:
                return Response({"success": False, "message": "Account Creation Failed",
                                 "data": "This Email address has been registered"},
                                status=status.HTTP_400_BAD_REQUEST)

            return Response({"success": False, "message": "Account Creation Failed",
                             "data": str(list(serializer.errors.keys())[0]) + ": " + str(
                                 list(serializer.errors.values())[0][0])},
                            status=status.HTTP_400_BAD_REQUEST)


class UserListAPI(generics.ListCreateAPIView):
    """
        Get Character List
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('id')

    def post(self, request, *args, **kwargs):
        """
            Get all Characters
            :param request: Service Records
            :param kwargs: NA
            :return: all Characters
    """
        paginator = AccountsPagination()
        page_size = paginator.page_size

        user_list = []
        user_data = User.objects.filter(is_admin=True, is_student=False)
        if user_data:
            for i in user_data:
                users_dict = {
                    "id": i.id if i.id else False,
                    "email": i.email if i.email else False,
                    "password": i.password if i.password else False,
                    "remarks": i.remarks if i.remarks else False,
                    "role_id": i.role_id.id if i.role_id else False,
                    "role_name": i.role_id.role_title if i.role_id else False,
                    "user_status": i.user_status if i.user_status else False,
                    "created_date": str(i.created_date),
                    "updated_date": str(i.updated_date)
                }
                user_list.append(users_dict)
            result_page = paginator.paginate_queryset(user_list, request)
            paginator_data = paginator.get_paginated_response(result_page).data
            if len(user_list) > 0:
                paginator_data['total_pages'] = math.ceil(len(result_page) / page_size)
            else:
                return Response({"success": False, "message": "No data"},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({
                "success": True,
                "message": "Success",
                "data": paginator_data,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Failed", "data": "Not Found"},
                            status=status.HTTP_400_BAD_REQUEST)


class ListAllUsersAPI(generics.ListCreateAPIView):
    """
        Get Character List
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('id')

    def post(self, request, *args, **kwargs):
        """
            Get all Characters
            :param request: Service Records
            :param kwargs: NA
            :return: all Characters
    """
        paginator = AccountsPagination()
        page_size = 10

        user_list = []
        user_data = User.objects.all()
        if user_data:
            for i in user_data:
                users_dict = {
                    "id": i.id if i.id else False,
                    "email": i.email if i.email else False,
                    "password": i.password if i.password else False,
                    "remarks": i.remarks if i.remarks else False,
                    "role_id": i.role_id.id if i.role_id else False,
                    "role_name": i.role_id.role_title if i.role_id else False,
                    "user_status": i.user_status if i.user_status else False,
                    "created_date": str(i.created_date),
                    "updated_date": str(i.updated_date)
                }
                user_list.append(users_dict)
            result_page = paginator.paginate_queryset(user_list, request)
            paginator_data = paginator.get_paginated_response(result_page).data
            if len(user_list) > 0:
                paginator_data['total_pages'] = math.ceil(len(result_page) / page_size)
            else:
                return Response({"success": False, "message": "No data"},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({
                "success": True,
                "message": "Success",
                "data": paginator_data,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Failed", "data": "Not Found"},
                            status=status.HTTP_400_BAD_REQUEST)


class UserFormAPI(generics.ListCreateAPIView):
    """
        Get Character List
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('id')

    def post(self, request, *args, **kwargs):
        """
            Get all Characters
            :param request: Service Records
            :param kwargs: NA
            :return: all Characters
    """

        account_id = request.data.get('id')
        user_data = User.objects.get(id=account_id)
        if user_data:
            i = user_data
            users_dict = {
                "id": i.id if i.id else False,
                "email": i.email if i.email else False,
                "password": i.password if i.password else False,
                "password_string": i.password_string if i.password_string else False,
                "remarks": i.remarks if i.remarks else False,
                "role_id": i.role_id.id if i.role_id else False,
                "role_name": i.role_id.role_title if i.role_id else False,
                "user_status": i.user_status if i.user_status else False,
                "created_date": str(i.created_date),
                "updated_date": str(i.updated_date)
            }

            return Response({
                "success": True,
                "message": "Success",
                "data": users_dict,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Failed", "data": "Not Found"},
                            status=status.HTTP_400_BAD_REQUEST)


class UserEditAPI(generics.ListCreateAPIView):
    """
        Get Character List
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = AdminRegisterSerializer
    queryset = User.objects.all().order_by('id')

    def post(self, request, **kwargs):
        """
        Updates snippets delete
        :param kwargs: snippets id
        :return: message
        """
        try:
            user_data = User.objects.get(id=request.data.get('id'))

            if user_data:
                if request.data.get('email'):
                    remove_current_account = User.objects.exclude(id=request.data.get('id')).order_by('-id')
                    user_exist = remove_current_account.filter(user_id=request.data.get('email'))
                    email_exist = remove_current_account.filter(email=request.data.get('email'))
                    if user_exist or email_exist:
                        return Response({"success": False, "message": "Account Creation Failed ",
                                         "data": "This Email address has been registered"},
                                        status=status.HTTP_404_NOT_FOUND)
                if request.data.get('email'):
                    user_data.email = request.data.get('email')
                if request.data.get('user_id'):
                    user_data.user_id = request.data.get('user_id')
                if request.data.get('password'):
                    user_data.set_password(request.data.get('password'))
                if request.data.get('role_id'):
                    user_data.role_id = RoleSetting.objects.get(id=request.data.get('role_id'))
                if request.data.get('remarks'):
                    user_data.remarks = request.data.get('remarks')
                if request.data.get('user_status'):
                    user_data.user_status = request.data.get('user_status')
                user_data.save()
                return Response({
                    "success": True,
                    "message": "Success",
                }, status=status.HTTP_200_OK)

            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class UserDeleteAPI(generics.ListCreateAPIView):
    """
        Get Character List
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('id')

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


class AdminPasswordReset(APIView):
    """
        Sent OTP to User and Token Generation
    """
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('-id')

    def post(self, request):
        email_id = request.data.get('email_id')
        number = random.randint(1111, 9999)

        if email_id:
            user_id = User.objects.filter(email=request.data.get('email_id')).first()
            if user_id:
                pass_url = uuid.uuid4()
                user_id.password_url = pass_url
                user_id.otp = number
                user_id.save()
                subject = 'First Time Login'
                english_name = ""
                if user_id.english_name:
                    english_name = user_id.english_name
                message = f'Hi {english_name}, Use the following OTP for first time login. OTP: {number}'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [email_id, ]
                send_mail(subject, message, email_from, recipient_list)
                url = "account/admin/token/" + str(user_id.password_url)
                return Response({"success": True, "message": "Reset OTP Sent", "data": {"submit_url": url},
                                 "token": AuthToken.objects.create(user_id)[1]},
                                status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "Fail to Send OTP", "data": "Sorry Invalid email"},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"success": False, "message": "Fail to Send OTP", "data": "Sorry Invalid email"},
                            status=status.HTTP_400_BAD_REQUEST)


class AdminResetTokenPasswordVerification(generics.ListCreateAPIView):
    """
        Otp and Token Verification
    """
    serializer_class = TokenSerializer
    queryset = User.objects.all().order_by('-id')

    @api_view(['POST'])
    def snippet_detail(request, token):
        """
        Retrieve, update or delete a code snippet.
        """
        try:
            snippet = User.objects.filter(password_url=token).first()
        except User.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'POST':
            if snippet.otp == request.data.get('otp'):
                pass_url = uuid.uuid4()
                pass_url2 = uuid.uuid4()
                snippet.password_set_url = pass_url
                snippet.otp = pass_url2
                snippet.password_url = pass_url2
                snippet.save()
                url = "account/admin/password/reset/" + str(snippet.password_set_url)
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": {
                        "password_reset_url": url
                    },
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "success": False,
                    "message": "OTP Verification Failed",
                    "data": {

                    },
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class AdminPasswordVerification(generics.ListCreateAPIView):
    """
        Password Reset
    """
    serializer_class = TokenSerializer
    queryset = User.objects.all().order_by('-id')

    @api_view(['POST'])
    def snippet_detail(request, token):
        """
            Retrieve, update or delete a code snippet.
        """
        try:
            snippet = User.objects.filter(password_set_url=token).first()
        except User.DoesNotExist:
            return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'POST':
            password = request.data.get('password')
            if password:
                snippet.set_password(password)
                pass_url = uuid.uuid4()
                snippet.password_set_url = pass_url
                snippet.save()
                return Response({
                    "success": True,
                    "message": "Password changed",
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "success": False,
                    "message": "Password reset failed",
                    "data": {

                    },
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response({"success": False, "message": "Not Found"},
                        status=status.HTTP_404_NOT_FOUND)


class AdminSignInAPI(generics.GenericAPIView):
    """
        Admin Login
    """
    serializer_class = AdminLoginSerializer

    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        if serializer.is_valid():
            user_val = serializer.validated_data
            if user_val.user_status is False:
                return Response({
                    "success": False,
                    "message": "Your account is deactivated",
                })
            return Response({
                "success": True,
                "message": "Successfully Logged In",
                "data":
                    {
                        "user": AdminLoginSerializer(user_val, context=self.get_serializer_context()).data,
                        "token": AuthToken.objects.create(user_val)[1],
                        "role": {
                            "all_privileges": user_val.role_id.all_privileges if user_val.role_id else "",
                            "records_approval": user_val.role_id.records_approval if user_val.role_id else "",
                            "records_approval_home": user_val.role_id.records_approval_home if user_val.role_id else "",
                            "records_approval_school": user_val.role_id.records_approval_school if user_val.role_id else "",
                            "records_approval_community": user_val.role_id.records_approval_community if user_val.role_id else "",
                            "post_services": user_val.role_id.post_services if user_val.role_id else "",
                            "post_services_teachers_sharing": user_val.role_id.post_services_teachers_sharing if user_val.role_id else "",
                            "post_services_school": user_val.role_id.post_services_school if user_val.role_id else "",
                            "post_services_community": user_val.role_id.post_services_community if user_val.role_id else "",
                            "monitoring": user_val.role_id.monitoring if user_val.role_id else "",
                            "monitoring_chat_room": user_val.role_id.monitoring_chat_room if user_val.role_id else "",
                            "monitoring_home_service": user_val.role_id.monitoring_home_service if user_val.role_id else "",
                            "monitoring_share_record_area": user_val.role_id.monitoring_share_record_area if user_val.role_id else "",
                            "service_record": user_val.role_id.service_record if user_val.role_id else "",
                            "service_record_import": user_val.role_id.service_record_import if user_val.role_id else "",
                            "service_record_export_full_list": user_val.role_id.service_record_export_full_list if user_val.role_id else "",
                            "service_record_export_individual_record": user_val.role_id.service_record_export_individual_record if user_val.role_id else "",
                            "service_record_add_student": user_val.role_id.service_record_add_student if user_val.role_id else "",
                            "redeemed_items": user_val.role_id.redeemed_items if user_val.role_id else "",
                            "redeem_item_list": user_val.role_id.redeem_item_list if user_val.role_id else "",
                            "redeem_item_record": user_val.role_id.redeem_item_record if user_val.role_id else "",
                            "role_setting": user_val.role_id.role_setting if user_val.role_id else "",
                            "add_role": user_val.role_id.add_role if user_val.role_id else "",
                            "edit_role": user_val.role_id.edit_role if user_val.role_id else "",
                            "delete_role": user_val.role_id.delete_role if user_val.role_id else "",
                            "is_active": user_val.role_id.is_active if user_val.role_id else ""
                        },
                    },
            }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Login Failed",
                             "data": str(list(serializer.errors.keys())[0]) + ": " + str(
                                 list(serializer.errors.values())[0][0])}, status=status.HTTP_400_BAD_REQUEST)


class RoleSettingView(generics.ListAPIView):

    def post(self, request):
        user_id = request.data.get('user_id')
        user_val = User.objects.get(id=user_id)

        return Response({
            "success": True,
            "message": "Roles View",
            "data":
                {
                    "user": AdminLoginSerializer(user_val, context=self.get_serializer_context()).data,
                    "role": {
                            "all_privileges": user_val.role_id.all_privileges if user_val.role_id else "",
                            "records_approval": user_val.role_id.records_approval if user_val.role_id else "",
                            "records_approval_home": user_val.role_id.records_approval_home if user_val.role_id else "",
                            "records_approval_school": user_val.role_id.records_approval_school if user_val.role_id else "",
                            "records_approval_community": user_val.role_id.records_approval_community if user_val.role_id else "",
                            "post_services": user_val.role_id.post_services if user_val.role_id else "",
                            "post_services_teachers_sharing": user_val.role_id.post_services_teachers_sharing if user_val.role_id else "",
                            "post_services_school": user_val.role_id.post_services_school if user_val.role_id else "",
                            "post_services_community": user_val.role_id.post_services_community if user_val.role_id else "",
                            "monitoring": user_val.role_id.monitoring if user_val.role_id else "",
                            "monitoring_chat_room": user_val.role_id.monitoring_chat_room if user_val.role_id else "",
                            "monitoring_home_service": user_val.role_id.monitoring_home_service if user_val.role_id else "",
                            "monitoring_share_record_area": user_val.role_id.monitoring_share_record_area if user_val.role_id else "",
                            "service_record": user_val.role_id.service_record if user_val.role_id else "",
                            "service_record_import": user_val.role_id.service_record_import if user_val.role_id else "",
                            "service_record_export_full_list": user_val.role_id.service_record_export_full_list if user_val.role_id else "",
                            "service_record_export_individual_record": user_val.role_id.service_record_export_individual_record if user_val.role_id else "",
                            "service_record_add_student": user_val.role_id.service_record_add_student if user_val.role_id else "",
                            "redeemed_items": user_val.role_id.redeemed_items if user_val.role_id else "",
                            "redeem_item_list": user_val.role_id.redeem_item_list if user_val.role_id else "",
                            "redeem_item_record": user_val.role_id.redeem_item_record if user_val.role_id else "",
                            "role_setting": user_val.role_id.role_setting if user_val.role_id else "",
                            "add_role": user_val.role_id.add_role if user_val.role_id else "",
                            "edit_role": user_val.role_id.edit_role if user_val.role_id else "",
                            "delete_role": user_val.role_id.delete_role if user_val.role_id else "",
                            "is_active": user_val.role_id.is_active if user_val.role_id else ""
                        }
                }
        }, status=status.HTTP_200_OK)


class TeacherList(APIView):
    """
        c List
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        teachers = User.objects.filter(is_teacher=True)
        serializer = UserSerializer(teachers, many=True)
        return Response(
            {"success": True, "message": "teachers Details", "data": serializer.data}, status=status.HTTP_200_OK)

    def post(self):
        pass


class StudentList(APIView):
    """
        Students List
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        students = User.objects.filter(is_student=True)
        serializer = UserSerializer(students, many=True)
        return Response(
            {"success": True, "message": "Students Details", "data": serializer.data}, status=status.HTTP_200_OK)

    def post(self):
        pass


class FormList(APIView):
    """
        Students List
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        forms = Form.objects.all()
        form_list = []
        if forms:
            for i in forms:
                form_dict = {
                    "id": i.id,
                    "form_name": i.form_name if i.form_name else "",
                    "active": i.active,
                    "created_date": str(i.created_date),
                    "updated_date": str(i.updated_date)
                }
                form_list.append(form_dict)
            return Response({
                "success": True,
                "message": "Form Details",
                "data": form_list},
                status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)

    def post(self):
        pass


class ClassList(APIView):
    """
        Students List
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        classes = Class.objects.all()
        classes_list = []
        if classes:
            for i in classes:
                form_dict = {
                    "id": i.id,
                    "class_name": i.class_name if i.class_name else "",
                    "form_id": i.form_id.id if i.form_id else "",
                    "form_name": i.form_id.form_name if i.form_id else "",
                    "active": i.active,
                    "created_date": str(i.created_date),
                    "updated_date": str(i.updated_date)
                }
                classes_list.append(form_dict)
            return Response({
                "success": True,
                "message": "Class Details",
                "data": classes_list},
                status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)

    def post(self):
        pass

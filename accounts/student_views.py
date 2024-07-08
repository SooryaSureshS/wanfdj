import random
import uuid
from knox.models import AuthToken
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.conf import settings
from accounts.models import User, UserLoginHistory, CharacterOwned
from .serializers import UserSerializer, TokenSerializer, StudentLoginSerializer
from django.core.mail import send_mail
from rest_framework.permissions import IsAuthenticated
from datetime import date
from character.models import Character
from django.core.exceptions import *
from service_records.models import ServiceRecords
from service_records.serializers import ServicesSerializer
from datetime import datetime
from application_service.serializers import ApplicationServiceApplicantsSerializer, NotificationSerializer
from application_service.models import ApplicationServiceApplicants, Notification


class StudentFirstTimeRegister(APIView):
    """
        Sent OTP to User and Token Generation
    """
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('-id')

    def post(self, request):
        email_id = request.data.get('email_id')
        number = random.randint(1111, 9999)

        if email_id:
            user_id = User.objects.filter(email=request.data.get('email_id'), is_student=True).first()
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
                url = "account/student/first/login/token/" + str(user_id.password_url)
                return Response({"success": True, "message": "Reset OTP Sent",
                                 "data": {"submit_url": url},
                                 "token": AuthToken.objects.create(user_id)[1]},
                                status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "Fail to Send OTP", "data": "Sorry Invalid email"},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"success": False, "message": "Fail to Send OTP", "data": "Sorry Invalid email"},
                            status=status.HTTP_400_BAD_REQUEST)


class StudentAccountTokenPasswordVerification(generics.ListCreateAPIView):
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
                url = "account/student/first/login/reset/" + str(snippet.password_set_url)
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


class StudentFirstTimeLoginVerification(generics.ListCreateAPIView):
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
                character = Character.objects.filter(character_type='normal').order_by('?').first()
                users_character = CharacterOwned.objects.filter(user_id=snippet)
                snippet.set_password(password)
                pass_url = uuid.uuid4()
                snippet.password_set_url = pass_url
                snippet.is_active = True
                snippet.save()
                if not users_character and character:
                    character_owned = CharacterOwned(user_id=snippet, character_id=character, active=True)
                    character_owned.save()
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


class StudentSignInAPI(generics.GenericAPIView):
    """
        Student Login
    """
    serializer_class = StudentLoginSerializer

    def post(self, request):
        try:
            serializer = StudentLoginSerializer(data=request.data)
            if serializer.is_valid():
                user_val = serializer.validated_data
                user_id = request.data.get('user_id')
                student_val = User.objects.get(user_id=user_id)
                new_status = student_val.is_new
                if student_val.user_status is False:
                    return Response({
                        "success": False,
                        "message": "Your account is deactivated",
                    })
                if student_val.is_new:
                    student_val.is_new = False
                    student_val.save()
                return Response({
                    "success": True,
                    "message": "Successfully Logged In",
                    "data":
                        {
                            "user": StudentLoginSerializer(user_val, context=self.get_serializer_context()).data,
                            "token": AuthToken.objects.create(user_val)[1],
                            "is_new": new_status
                        },
                }, status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "Login Failed",
                                 "data": str(list(serializer.errors.keys())[0]) + ": " + str(
                                     list(serializer.errors.values())[0][0])}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({
                "success": True,
                "message": "Login Failed",
                "data": {},
            }, status=status.HTTP_400_BAD_REQUEST)


class StudentHome(generics.GenericAPIView):
    """
        Student Login Log Create
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = StudentLoginSerializer

    def post(self, request):
        try:
            user_id = request.data.get('user_id')
            user_data = User.objects.filter(id=user_id).first()
            login_points = user_data.login_points
            if user_data and user_data.is_student:
                snippet = UserLoginHistory.objects.filter(user_id=user_data.id, created_date=date.today()).first()
                if snippet:
                    return Response({
                        "success": False,
                        "message": "Today's Log Already Exists",
                        "data": {},
                    }, status=status.HTTP_400_BAD_REQUEST)

                else:
                    user_login = UserLoginHistory.objects.create(user_id=user_data)
                    user_login.save()
                    user_data.login_points = login_points + 5
                    user_data.save()
                    return Response({
                        "success": True,
                        "message": "Points Added",
                        "data": {},
                    }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "success": False,
                    "message": "Invalid User",
                    "data": {},
                }, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({
                "success": True,
                "message": "Not Found",
                "data": {},
            }, status=status.HTTP_400_BAD_REQUEST)


class StudentProfileView(generics.GenericAPIView):
    """
        Student Profile View
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = StudentLoginSerializer
    serializer_class1 = ServicesSerializer
    queryset1 = ServiceRecords.objects.all().order_by('id')
    serializer_class2 = NotificationSerializer
    queryset2 = Notification.objects.all().order_by('-id')

    def post(self, request):
        try:
            http_layer = request.is_secure() and "https" or "http"
            http_address = request.get_host()
            urls = str(http_layer + "://" + http_address)
            user_id = request.data.get('user_id')
            user_data = User.objects.filter(id=user_id).first()
            school_service = ServiceRecords.objects.filter(service_type="school", user_id=user_id)
            home_service = ServiceRecords.objects.filter(service_type="home", user_id=user_id)
            community_service = ServiceRecords.objects.filter(service_type="community", user_id=user_id)

            snippets1 = self.queryset1.filter(user_id=user_data).order_by('-id')
            snippets2 = self.queryset2.filter(student_id=user_data).order_by('-id')
            count = 0
            record_count = 0

            school_service_hrs = 0
            home_service_hrs = 0
            community_service_hrs = 0
            if school_service:
                for i in school_service:
                    if i.service_duration and i.approval_status == "approved":
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
                    if i.service_duration and i.approval_status == "approved":
                        formatted_time = datetime.strptime(i.service_duration, '%H:%M:%S.%f').time()
                        hour_school = formatted_time.hour
                        minute_school = formatted_time.minute
                        school_time = hour_school * 60 + minute_school
                        total_hrs = 0
                        if school_time > 0:
                            total_hrs = school_time / 60
                        home_service_hrs = round(home_service_hrs + total_hrs, 2)
            if community_service:
                for i in community_service:
                    if i.service_duration and i.approval_status == "approved":
                        formatted_time = datetime.strptime(i.service_duration, '%H:%M:%S.%f').time()
                        hour_school = formatted_time.hour
                        minute_school = formatted_time.minute
                        school_time = hour_school * 60 + minute_school
                        total_hrs = 0
                        if school_time > 0:
                            total_hrs = school_time / 60
                        community_service_hrs = round(community_service_hrs + total_hrs, 2)
            i = user_data
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

            if user_data or snippets1 or snippets2:
                for k in snippets1:
                    if k.approval_status == 'disapproved':
                        record_count = record_count + 1
                    if k.notification_opened_status is False and k.disapproval_status is True:
                        count = count + 1
                for j in snippets2:
                    if j.approval_status == 'approved' or j.approval_status == 'disapproved':
                        record_count = record_count + 1
                    if j.notification_opened_status is False and j.approval_status == 'approved':
                        count = count + 1
                    if j.notification_opened_status is False and j.approval_status == 'disapproved':
                        count = count + 1
                vals = {
                    "id": i.id,
                    "user_id": i.user_id if i.user_id else False,
                    "student_id": i.student_id if i.student_id else False,
                    "english_name": i.english_name if i.english_name else "",
                    "chinese_name": i.chinese_name if i.chinese_name else "",
                    "personal_profile": i.personal_profile if i.personal_profile else "",
                    "email": i.student_id if i.student_id else "",
                    "sequence": i.sequence if i.sequence else "",
                    "phone": i.phone if i.phone else "",
                    "form_id": i.form_id.id if i.form_id else "",
                    "form_name": i.form_id.form_name if i.form_id else "",
                    "class_no": i.class_no if i.class_no else "",
                    "class_id": i.class_id.id if i.class_id else "",
                    "class_name": i.class_id.class_name if i.class_id else "",
                    "gender": i.gender if i.gender else "",
                    "birth_date": i.birth_date if i.birth_date else "",
                    "profile_picture": urls + "/account/media/" + str(
                        i.profile_picture) if i.profile_picture else "",
                    "home_service_duration": home_service_hrs_val if home_service_hrs_val else "0",
                    "school_service_duration": school_service_hrs_val if school_service_hrs_val else "0",
                    "community_service_duration": community_service_hrs_val if community_service_hrs_val else "0",
                    "registration_date": i.registration_date if i.registration_date else False,
                    "user_status": i.user_status,
                    "login_points": i.login_points if i.login_points else 0,
                    "student_rubies": i.student_rubies if i.student_rubies else 0,
                    "student_vitality": i.student_vitality if i.student_vitality else 0,
                    "student_exp": i.student_exp if i.student_exp else 0,
                    "is_active": i.is_active,
                    "is_admin": i.is_admin,
                    "is_staff": i.is_staff,
                    "is_student": i.is_student,
                    "created_date": str(i.created_date),
                    "updated_date": str(i.updated_date),
                    "unopened_notifications": count,
                    "record_count": record_count,

                }
                return Response({
                    "success": True,
                    "message": "Success",
                    "unopened_notifications": count,
                    "record_count": record_count,
                    "data": vals,
                }, status=status.HTTP_200_OK)

            else:
                return Response({
                    "success": False,
                    "message": "Invalid User",
                    "data": {},
                }, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({
                "success": True,
                "message": "Not Found",
                "data": {},
            }, status=status.HTTP_400_BAD_REQUEST)


class StudentProfileEdit(generics.GenericAPIView):
    """
        Student Profile Edit
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = StudentLoginSerializer

    def post(self, request):
        try:
            http_layer = request.is_secure() and "https" or "http"
            http_address = request.get_host()
            urls = str(http_layer + "://" + http_address)
            user_id = request.data.get('user_id')
            personal_profile = request.data.get('personal_profile')
            user_data = User.objects.filter(id=user_id).first()
            school_service = ServiceRecords.objects.filter(service_type="school", user_id=user_id)
            home_service = ServiceRecords.objects.filter(service_type="home", user_id=user_id)
            community_service = ServiceRecords.objects.filter(service_type="community", user_id=user_id)
            school_service_hrs = 0
            home_service_hrs = 0
            community_service_hrs = 0
            if school_service:
                for i in school_service:
                    if i.service_duration and i.approval_status == "approved":
                        formatted_time = datetime.strptime(i.service_duration, '%H:%M:%S.%f').time()
                        hour_school = formatted_time.hour
                        minute_school = formatted_time.minute
                        school_time = hour_school * 60 + minute_school
                        total_hrs = 0
                        if school_time > 0:
                            total_hrs = school_time / 60
                        school_service_hrs = round((school_service_hrs + total_hrs), 2)
            if home_service:
                for i in home_service:
                    if i.service_duration and i.approval_status == "approved":
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
                    if i.service_duration and i.approval_status == "approved":
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

            if user_data:
                user_data.personal_profile = personal_profile
                user_data.save()
                i = User.objects.filter(id=user_id).first()
                vals = {
                    "id": i.id,
                    "user_id": i.user_id if i.user_id else False,
                    "student_id": i.student_id if i.student_id else False,
                    "english_name": i.english_name if i.english_name else "",
                    "chinese_name": i.chinese_name if i.chinese_name else "",
                    "personal_profile": i.personal_profile if i.personal_profile else "",
                    "email": i.student_id if i.student_id else "",
                    "sequence": i.sequence if i.sequence else "",
                    "phone": i.phone if i.phone else "",
                    "class_no": i.class_no if i.class_no else "",
                    "class_id": i.class_id.id if i.class_id else "",
                    "class_name": i.class_id.class_name if i.class_id else "",
                    "gender": i.gender if i.gender else "",
                    "birth_date": i.birth_date if i.birth_date else "",
                    "profile_picture": urls + "/account/media/" + str(
                        i.profile_picture) if i.profile_picture else "",
                    "home_service_duration": home_service_hrs_val if home_service_hrs_val else "0",
                    "school_service_duration": school_service_hrs_val if school_service_hrs_val else "0",
                    "community_service_duration": community_service_hrs_val if community_service_hrs_val else "0",
                    "registration_date": i.registration_date if i.registration_date else False,
                    "user_status": i.user_status,
                    "login_points": i.login_points if i.login_points else 0,
                    "student_rubies": i.student_rubies if i.student_rubies else 0,
                    "student_vitality": i.student_vitality if i.student_vitality else 0,
                    "student_exp": i.student_exp if i.student_exp else 0,
                    "is_active": i.is_active,
                    "is_admin": i.is_admin,
                    "is_staff": i.is_staff,
                    "is_student": i.is_student,
                    "created_date": str(i.created_date),
                    "updated_date": str(i.updated_date)
                }
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": vals,
                }, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({
                    "success": False,
                    "message": "Invalid User",
                    "data": {},
                }, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({
                "success": False,
                "message": "Not Found",
                "data": {},
            }, status=status.HTTP_400_BAD_REQUEST)


class RandomCharacterSelection(APIView):
    """
        Sent OTP to User and Token Generation
    """
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('-id')

    def post(self, request):
        user_id = request.data.get('user_id')
        print(user_id)
        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)
        normal_character = Character.objects.filter(character_type="normal")
        random_character = random.choice(normal_character)

        if user_id:
            user = User.objects.filter(id=user_id, is_student=True)
            print(user)
            ran_chara = Character.objects.get(name=random_character)
            if user:
                character_owned = CharacterOwned(user_id_id=user_id, character_id=ran_chara, character_name=ran_chara.name, active=True)
                character_owned.character_hp += 100
                challenge = random.randint(7, 13)
                character_owned.critical += challenge
                character_owned.dodge += 2
                character_owned.save()
                return Response({"success": True,
                                 "random_character": urls + "/service/records/media/" + str(ran_chara.character_image)},
                                status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "Failed"},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"success": False, "message": "Failed"},
                            status=status.HTTP_400_BAD_REQUEST)

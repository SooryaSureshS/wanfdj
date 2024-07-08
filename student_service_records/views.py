from rest_framework import status, generics
from knox.models import AuthToken
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.response import Response
from accounts.serializers import UserSerializer, StudentCreateSerializer
from service_records.serializers import ServicesSerializer
from accounts.models import User, Form, Class
from service_records.models import ServiceRecords
from rest_framework.permissions import IsAuthenticated
from .pagination import StudentServiceRecordsPagination
import math
import datetime
from datetime import datetime as dt
from student_service_records.serializers import ClassesSerializers


class AddStudents(generics.GenericAPIView):
    serializer_class = StudentCreateSerializer
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def post(self, request, *args, **kwargs):
        if not request.user.student_id:
            if request.user.role_id is None:
                return Response({"success": False, "message": "User has no role id set"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not (request.user.role_id.all_privileges or (request.user.role_id.service_record or request.user.role_id.service_record_add_student)):
                return Response({"success": False, "message": "User has no privilege"},
                                status=status.HTTP_400_BAD_REQUEST)

        serializer = StudentCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "success": True,
                "message": "Account Created",
                "data":
                    {
                        "user": StudentCreateSerializer(user, context=self.get_serializer_context()).data,
                        "student_password": request.data.get('password'),
                        "token": AuthToken.objects.create(user)[1]
                    },
                }, status=status.HTTP_200_OK)
        else:
            email = request.data.get('email')
            email_exist = User.objects.filter(email=email).exists()
            student_id = request.data.get('student_id')
            student_id_exist = User.objects.filter(student_id=student_id).exists()
            if email_exist:
                return Response({"success": False, "message": "Account Creation Failed",
                                 "data": "This Email address has been registered"},
                                status=status.HTTP_400_BAD_REQUEST)
            if student_id_exist:
                return Response({"success": False, "message": "Account Creation Failed",
                                 "data": "This Student Id has been registered"},
                                status=status.HTTP_400_BAD_REQUEST)

            return Response({"success": False, "message": "Account Creation Failed",
                             "data": str(list(serializer.errors.keys())[0]) + ": " + str(
                                 list(serializer.errors.values())[0][0])},
                            status=status.HTTP_400_BAD_REQUEST)


class StudentForm(generics.ListCreateAPIView):
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
        school_service = ServiceRecords.objects.filter(service_type="school", user_id=user_data.id)
        home_service = ServiceRecords.objects.filter(service_type="home", user_id=user_data.id)
        community_service = ServiceRecords.objects.filter(service_type="community", user_id=user_data.id)
        school_service_hrs = 0
        home_service_hrs = 0
        community_service_hrs = 0
        if school_service:
            for i in school_service:
                if i.service_duration and i.approval_status == "approved":
                    formatted_time = dt.strptime(i.service_duration, '%H:%M:%S.%f').time()
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
                    formatted_time = dt.strptime(i.service_duration, '%H:%M:%S.%f').time()
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
                    formatted_time = dt.strptime(i.service_duration, '%H:%M:%S.%f').time()
                    hour_school = formatted_time.hour
                    minute_school = formatted_time.minute
                    school_time = hour_school * 60 + minute_school
                    total_hrs = 0
                    if school_time > 0:
                        total_hrs = school_time / 60
                    community_service_hrs = community_service_hrs + total_hrs

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
            i = user_data
            users_dict = {
                "id": i.id,
                "user_id": i.user_id if i.user_id else False,
                "user_name": i.user_id if i.user_id else False,
                "english_name": i.english_name if i.english_name else "",
                "chinese_name": i.chinese_name if i.chinese_name else "",
                "student_id": i.student_id if i.student_id else "",
                "email": i.email if i.email else "",
                "class_no": i.class_no if i.class_no else "",
                "class_id": i.class_id.id if i.class_id else "",
                "class_name": i.class_id.class_name if i.class_id else "",
                "birth_date": i.birth_date if i.birth_date else "",
                "gender": i.gender if i.gender else "",
                "form_id": i.form_id.id if i.form_id else "",
                "form_name": i.form_id.form_name if i.form_id else "",
                "password": i.password if i.password else "",
                "password_string": i.password_string if i.password_string else "",
                "personal_profile": i.personal_profile if i.personal_profile else "",
                "home_service_duration": home_service_hrs_val if home_service_hrs_val else "",
                "school_service_duration": school_service_hrs_val if school_service_hrs_val else "",
                "community_service_duration": community_service_hrs_val if community_service_hrs_val else "",
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


class StudentUpdate(generics.ListCreateAPIView):
    """
        Get Character List
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = StudentCreateSerializer
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
                student_id = request.data.get('student_id')
                remove_current_account = User.objects.exclude(id=request.data.get('id')).order_by('-id')
                email_exist = remove_current_account.filter(email=request.data.get('email'))
                student_id_exist = remove_current_account.filter(student_id=student_id).exists()
                if email_exist:
                    return Response({"success": False, "message": "Account Creation Failed",
                                     "data": "This Email address has been registered"},
                                    status=status.HTTP_400_BAD_REQUEST)
                if student_id_exist:
                    return Response({"success": False, "message": "Account Creation Failed",
                                     "data": "This Student Id has been registered"},
                                    status=status.HTTP_400_BAD_REQUEST)
                form_data = Form.objects.get(id=request.data.get('form_id'))
                class_data = Class.objects.get(id=request.data.get('class_id'))
                if request.data.get('english_name'):
                    user_data.english_name = request.data.get('english_name')
                if request.data.get('chinese_name'):
                    user_data.chinese_name = request.data.get('chinese_name')
                if request.data.get('student_id'):
                    user_data.student_id = request.data.get('student_id')
                if request.data.get('email'):
                    user_data.user_id = request.data.get('email')
                if request.data.get('email'):
                    user_data.email = request.data.get('email')
                if request.data.get('class_no'):
                    user_data.class_no = request.data.get('class_no')
                if request.data.get('password'):
                    user_data.set_password(request.data.get('password'))
                if request.data.get('class_no'):
                    user_data.class_no = request.data.get('class_no')
                if request.data.get('form_id'):
                    user_data.form_id = form_data
                if request.data.get('class_id'):
                    user_data.class_id = class_data
                if request.data.get('gender'):
                    user_data.gender = request.data.get('gender')
                if request.data.get('birth_date'):
                    dob = datetime.datetime.strptime(request.data.get('birth_date'), '%d/%m/%Y').strftime('%Y-%m-%d')
                    user_data.birth_date = dob
                if request.data.get('personal_profile'):
                    user_data.personal_profile = request.data.get('personal_profile')
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


class StudentRecordsFilter(generics.ListCreateAPIView):
    """
      All Service Records
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('id')

    def post(self, request, *args, **kwargs):
        """
            Get all Student Records Filter
            :param request: Student Records Filter
            :param kwargs: NA
            :return: Service Records
        """
        form = request.data.get('form')
        year = request.data.get('year')
        classes = request.data.get('classes')

        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        paginator = StudentServiceRecordsPagination()
        page_size = paginator.page_size

        snippets = self.queryset.all().order_by("-id")
        service_records = []
        if request.data.get('form') and request.data.get('classes'):
            snippets = self.queryset.filter(form_id__id=form, class_id__class_name=classes)
        elif request.data.get('form'):
            snippets = self.queryset.filter(form_id__id=form)
        else:
            snippets = self.queryset.all().order_by("-id")

        if snippets:
            for i in snippets:
                if i.user_id and i.is_student:
                    school_service = ServiceRecords.objects.filter(user_id=i.id, service_type="school")
                    home_service = ServiceRecords.objects.filter(user_id=i.id, service_type="home")
                    community_service = ServiceRecords.objects.filter(user_id=i.id, service_type="community")
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

                    total_community_home = home_service_hrs + community_service_hrs
                    total_community_home_school =home_service_hrs + community_service_hrs + school_service_hrs

                    total_community_home_hours = int(total_community_home)
                    total_community_home_minutes = int((total_community_home * 60) % 60)
                    total_community_home_val = str(total_community_home_hours) + ":" + str(total_community_home_minutes)

                    total_community_home_school_hours = int(total_community_home_school)
                    total_community_home_school_minutes = int((total_community_home_school * 60) % 60)
                    total_community_home_school_val = str(total_community_home_school_hours) + ":" + str(total_community_home_school_minutes)

                    if total_community_home == 0:
                        total_community_home_val = "0"
                    if total_community_home_school == 0:
                        total_community_home_school_val = "0"

                    service_vals = {
                        "id": i.id,
                        "user_id": i.user_id if i.user_id else False,
                        "user_name": i.user_id if i.user_id else False,
                        "english_name": i.english_name if i.english_name else "",
                        "chinese_name": i.chinese_name if i.chinese_name else "",
                        "student_id": i.student_id if i.student_id else "",
                        "email": i.email if i.email else "",
                        "form_id": i.form_id.id if i.form_id else "",
                        "form_name": i.form_id.form_name if i.form_id else "",
                        "class_no": i.class_no if i.class_no else "",
                        "class_id": i.class_id.id if i.class_id else "",
                        "class_name": i.class_id.class_name if i.class_id else "",
                        "home_and_community_service": total_community_home_val if total_community_home_val else "0",
                        "total_service_hr_this_year": total_community_home_school_val if total_community_home_school_val else "0",
                        "total_service_hr_from_f1": total_community_home_school_val if total_community_home_school_val else "0",
                        "user_status": i.user_status if i.user_status else False,
                        "created_date": str(i.created_date),
                        "updated_date": str(i.updated_date)
                    }
                    service_records.append(service_vals)
            sorted_service_records = sorted(service_records, key=lambda y: y['class_no'], reverse=True)

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


class StudentRecordsList(generics.ListCreateAPIView):
    """
      All Service Records
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('id')

    def post(self, request, *args, **kwargs):
        """
            Get all Student Records Filter
            :param request: Student Records Filter
            :param kwargs: NA
            :return: Service Records
        """
        form = request.data.get('form')
        year = request.data.get('year')
        classes = request.data.get('classes')

        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        print("http_address", http_address)
        print("META-------------", request.META)
        print("request dict-------------", request.__dict__)
        urls = str(http_layer + "://" + http_address)

        snippets = self.queryset.all().order_by("-id")
        service_records = []

        if snippets:
            for i in snippets:
                if i.user_id and i.is_student:
                    school_service = ServiceRecords.objects.filter(user_id=i.id, service_type="school")
                    home_service = ServiceRecords.objects.filter(user_id=i.id, service_type="home")
                    community_service = ServiceRecords.objects.filter(user_id=i.id, service_type="community")
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

                    total_community_home = home_service_hrs + community_service_hrs
                    total_community_home_school =home_service_hrs + community_service_hrs + school_service_hrs

                    total_community_home_hours = int(total_community_home)
                    total_community_home_minutes = int((total_community_home * 60) % 60)
                    total_community_home_val = str(total_community_home_hours) + ":" + str(total_community_home_minutes)

                    total_community_home_school_hours = int(total_community_home_school)
                    total_community_home_school_minutes = int((total_community_home_school * 60) % 60)
                    total_community_home_school_val = str(total_community_home_school_hours) + ":" + str(total_community_home_school_minutes)

                    if total_community_home == 0:
                        total_community_home_val = "0"
                    if total_community_home_school == 0:
                        total_community_home_school_val = "0"

                    service_vals = {
                        "id": i.id,
                        "user_id": i.user_id if i.user_id else False,
                        "user_name": i.user_id if i.user_id else False,
                        "english_name": i.english_name if i.english_name else "",
                        "chinese_name": i.chinese_name if i.chinese_name else "",
                        "student_id": i.student_id if i.student_id else "",
                        "email": i.email if i.email else "",
                        "form_id": i.form_id.id if i.form_id else "",
                        "form_name": i.form_id.form_name if i.form_id else "",
                        "class_no": i.class_no if i.class_no else "",
                        "class_id": i.class_id.id if i.class_id else "",
                        "class_name": i.class_id.class_name if i.class_id else "",
                        "home_and_community_service": total_community_home_val if total_community_home_val else "0",
                        "total_service_hr_this_year": total_community_home_school_val if total_community_home_school_val else "0",
                        "total_service_hr_from_f1": total_community_home_school_val if total_community_home_school_val else "0",
                        "user_status": i.user_status if i.user_status else False,
                        "created_date": str(i.created_date),
                        "updated_date": str(i.updated_date)
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


class StudentServiceHome(generics.ListCreateAPIView):
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
        student_id = request.data.get('id')
        service_date = request.data.get('service_date')
        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        if service_date:
            snippets = self.queryset.filter(user_id=student_id, service_type='home',
                                            serving_date=service_date).order_by('id')
        else:
            snippets = self.queryset.filter(service_type='home', user_id=student_id)
        service_records = []

        if snippets:
            for i in snippets:
                if i.user_id and i.user_id.is_student:
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
            return Response({
                "success": True,
                "message": "Success",
                "data": service_records,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class StudentServiceCommunity(generics.ListCreateAPIView):
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
        student_id = request.data.get('id')
        service_date = request.data.get('service_date')
        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        if service_date:
            snippets = self.queryset.filter(user_id=student_id, service_type='community',
                                            serving_date=service_date).order_by('id')
        else:
            snippets = self.queryset.filter(service_type='community', user_id=student_id)
        service_records = []

        if snippets:
            for i in snippets:
                if i.user_id and i.user_id.is_student:
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
            return Response({
                "success": True,
                "message": "Success",
                "data": service_records,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class StudentServiceSchool(generics.ListCreateAPIView):
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
        student_id = request.data.get('id')
        service_date = request.data.get('service_date')
        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        if service_date:
            snippets = self.queryset.filter(user_id=student_id, service_type='school',
                                            serving_date=service_date).order_by('id')
        else:
            snippets = self.queryset.filter(service_type='school', user_id=student_id)
        service_records = []

        if snippets:
            for i in snippets:
                if i.user_id and i.user_id.is_student:
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
            return Response({
                "success": True,
                "message": "Success",
                "data": service_records,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class StudentServiceHomeItem(generics.ListCreateAPIView):
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
        student_id = request.data.get('id')
        record_id = request.data.get('record_id')
        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        snippets = self.queryset.filter(id=record_id, service_type='home', user_id=student_id)
        service_records = []

        if snippets:
            for i in snippets:
                if i.user_id and i.user_id.is_student:
                    service_vals = {
                        "id": i.id,
                        "user_id": i.user_id.id if i.user_id else False,
                        "user_name": i.user_id.user_id if i.user_id else False,
                        "user_english_name": i.user_id.english_name if i.user_id else False,
                        "student_id": i.user_id.student_id if i.user_id else False,
                        "class_no": i.user_id.class_no if i.user_id else False,
                        "class_name": i.user_id.class_name if i.user_id else False,
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
                    return Response({
                        "success": True,
                        "message": "Success",
                        "data": service_vals,
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({"success": False, "message": "Not Found", "data": {}},
                                    status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class StudentServiceCommunityItem(generics.ListCreateAPIView):
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
        student_id = request.data.get('id')
        record_id = request.data.get('record_id')
        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        snippets = self.queryset.filter(id=record_id, service_type='community', user_id=student_id)
        service_records = []

        if snippets:
            for i in snippets:
                if i.user_id and i.user_id.is_student:
                    service_vals = {
                        "id": i.id,
                        "user_id": i.user_id.id if i.user_id else False,
                        "user_name": i.user_id.user_id if i.user_id else False,
                        "user_english_name": i.user_id.english_name if i.user_id else False,
                        "student_id": i.user_id.student_id if i.user_id else False,
                        "class_no": i.user_id.class_no if i.user_id else False,
                        "class_name": i.user_id.class_name if i.user_id else False,
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
                    return Response({
                        "success": True,
                        "message": "Success",
                        "data": service_vals,
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({"success": False, "message": "Not Found", "data": {}},
                                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class StudentServiceSchoolItem(generics.ListCreateAPIView):
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
        student_id = request.data.get('id')
        record_id = request.data.get('record_id')
        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        snippets = self.queryset.filter(id=record_id, service_type='school', user_id=student_id)
        service_records = []

        if snippets:
            for i in snippets:
                if i.user_id and i.user_id.is_student:
                    service_vals = {
                        "id": i.id,
                        "user_id": i.user_id.id if i.user_id else False,
                        "user_name": i.user_id.user_id if i.user_id else False,
                        "user_english_name": i.user_id.english_name if i.user_id else False,
                        "student_id": i.user_id.student_id if i.user_id else False,
                        "class_no": i.user_id.class_no if i.user_id else False,
                        "class_name": i.user_id.class_name if i.user_id else False,
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
                    return Response({
                        "success": True,
                        "message": "Success",
                        "data": service_vals,
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({"success": False, "message": "Not Found", "data": {}},
                                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class FormClassesFilter(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ClassesSerializers
    queryset = Class.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        form = request.data.get('form')
        classes = []
        if form == '' or form is None:
            form = Form.objects.all().order_by('-id')
            if form:
                for j in form:
                    service_vals = {
                        "id": j.id,
                        "form_name": j.form_name if j.form_name else False
                    }
                    classes.append(service_vals)
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": classes,
                }, status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "Not Found", "data": {}},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            snippets = self.queryset.filter(form_id_id=form)
            if snippets:
                for i in snippets:
                    service_vals = {
                        "id": i.id,
                        "form_id": i.form_id.id if i.form_id else False,
                        "class_name": i.class_name if i.class_name else False,
                        "created_date": str(i.created_date),
                        "updated_date": str(i.updated_date)
                    }
                    classes.append(service_vals)
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": classes,
                }, status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "Not Found", "data": {}},
                                status=status.HTTP_400_BAD_REQUEST)


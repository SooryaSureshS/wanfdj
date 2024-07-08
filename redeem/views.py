from rest_framework import status, generics
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.response import Response
from .serializers import RedeemSerializer, RedeemRecordsSerializer
from .models import Redeem, RedeemRecord
from accounts.models import User, Form, Class
from rest_framework.permissions import IsAuthenticated
from .pagination import RedeemPagination
import math
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404


class RedeemAPI(generics.ListCreateAPIView):
    """
        List and Create Application Services
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = RedeemSerializer
    queryset = Redeem.objects.all().order_by('id')

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
            create Redeem
            :param request: Redeem
            :param kwargs: NA
            :return: Redeem details
        """
        if not request.user.student_id:
            if request.user.role_id is None:
                return Response({"success": False, "message": "User has no role id set"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not (request.user.role_id.all_privileges or (
                    request.user.role_id.redeemed_items and request.user.role_id.redeem_item_list and request.user.role_id.redeem_item_record)):
                return Response({"success": False, "message": "User has no privilege to redeem item list"},
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


class RedeemItemListAPI(generics.ListCreateAPIView):
    """
        Get Student Service List
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = RedeemSerializer
    queryset = Redeem.objects.all().order_by('id')

    def post(self, request, *args, **kwargs):
        """
            Get all Redeem Filter
            :param request: Redeem Records
            :param kwargs: NA
            :return: Redeem Records
        """
        if not request.user.student_id:
            if request.user.role_id is None:
                return Response({"success": False, "message": "User has no role id set"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not (request.user.role_id.all_privileges or request.user.role_id.redeem_item_list):
                return Response({"success": False, "message": "User has no privilege to redeem item list"},
                                status=status.HTTP_400_BAD_REQUEST)

        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        paginator = RedeemPagination()
        page_size = paginator.page_size

        snippets = self.queryset.all()
        redeem_records = []
        seq = 1

        if snippets:
            for i in snippets:
                redeem_vals = {
                    "id": i.id if i.id else False,
                    "sequence": seq,
                    "item_name": i.item_name if i.item_name else False,
                    "rubies": i.rubies if i.rubies else False,
                    "introduction": i.introduction if i.introduction else "",
                    "stock": i.stock if i.stock else False,
                    "value": i.value if i.value else False,
                    "amount": i.amount if i.amount else False,
                    "teachers_name": i.teachers_name if i.teachers_name else False,
                    "icon":  urls + "/media/" + str(i.icon) if i.icon else "",
                    "status": i.status if i.status else False,
                    "redeem_type": i.redeem_type if i.redeem_type else "",
                    "created_date": str(i.created_date),
                    "updated_date": str(i.updated_date)
                }
                redeem_records.append(redeem_vals)
                seq = seq + 1

            result_page = paginator.paginate_queryset(redeem_records, request)
            paginator_data = paginator.get_paginated_response(result_page).data
            if len(redeem_records) > 0:
                paginator_data['total_pages'] = math.ceil(len(redeem_records) / page_size)
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


class RedeemItemFormAPI(generics.ListCreateAPIView):
    """
        Redeem item Form
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = RedeemSerializer
    queryset = Redeem.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Get Redeem Item
            :param request: Id
            :param kwargs: NA
            :return: Redeem Record
        """
        if not request.user.student_id:
            if request.user.role_id is None:
                return Response({"success": False, "message": "User has no role id set"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not (request.user.role_id.all_privileges or request.user.role_id.redeem_item_list):
                return Response({"success": False, "message": "User has no privilege to redeem item form"},
                                status=status.HTTP_400_BAD_REQUEST)
        redeem_id = request.data.get('id')

        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        snippets = self.queryset.filter(id=redeem_id).first()

        if snippets:
            i = snippets
            redeem_vals = {
                "id": i.id if i.id else False,
                "item_name": i.item_name if i.item_name else False,
                "rubies": i.rubies if i.rubies else False,
                "introduction": i.introduction if i.introduction else "",
                "stock": i.stock if i.stock else False,
                "value": i.value if i.value else False,
                "amount": i.amount if i.amount else False,
                "teachers_name": i.teachers_name if i.teachers_name else False,
                "icon": urls + "/media/" + str(i.icon) if i.icon else False,
                "status": i.status if i.status else False,
                "redeem_type": i.redeem_type if i.redeem_type else "",
                "created_date": str(i.created_date),
                "updated_date": str(i.updated_date)
            }
            return Response({
                "success": True,
                "message": "Success",
                "data": redeem_vals,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class RedeemRecordAPI(generics.ListCreateAPIView):
    """
        List and Create Application Services
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = RedeemRecordsSerializer
    queryset = RedeemRecord.objects.all().order_by('id')

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

    def get(self, request):
        if self.request.user.role_id is None:
            return Response({"success": False, "message": "User has no role id set"},
                            status=status.HTTP_400_BAD_REQUEST)
        if not (self.request.user.role_id.all_privileges or self.request.user.role_id.redeem_item_record):
            return Response({"success": False, "message": "User has no privilege to redeem item record"},
                            status=status.HTTP_400_BAD_REQUEST)
        redeem_records = RedeemRecord.objects.all().order_by('id')
        serializer = RedeemRecordsSerializer(redeem_records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
            create Redeem
            :param request: Redeem
            :param kwargs: NA
            :return: Redeem details
        """
        if not request.user.student_id:
            if request.user.role_id is None:
                return Response({"success": False, "message": "User has no role id set"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not (request.user.role_id.all_privileges or request.user.role_id.redeem_item_record):
                return Response({"success": False, "message": "User has no privilege to redeem item record"},
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
            if request.data.get('status') == "approved":
                user_obj = User.objects.get(id=serializer.data.get('student_id'))
                redeem_obj = Redeem.objects.get(id=serializer.data.get('item_id'))
                user_obj.student_rubies -= redeem_obj.rubies
                redeem_obj.stock -= 1
                user_obj.save()
                redeem_obj.save()
            return Response({
                "success": True,
                "message": "Success",
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED)
        return Response({"success": False, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class RedeemRecordListAPI(generics.ListCreateAPIView):
    """
        Get Student Service List
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = RedeemRecordsSerializer
    queryset = RedeemRecord.objects.all().order_by('id')

    def post(self, request, *args, **kwargs):
        """
            Get all Redeem Filter
            :param request: Redeem Records
            :param kwargs: NA
            :return: Redeem Records
        """
        if not request.user.student_id:
            if request.user.role_id is None:
                return Response({"success": False, "message": "User has no role id set"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not (request.user.role_id.all_privileges or request.user.role_id.redeem_item_record):
                return Response({"success": False, "message": "User has no privilege to redeem item record"},
                                status=status.HTTP_400_BAD_REQUEST)

        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        paginator = RedeemPagination()
        page_size = paginator.page_size

        snippets = self.queryset.all()
        redeem_records = []
        seq = 1

        if snippets:
            for i in snippets:
                redeem_vals = {
                    "id": i.id if i.id else False,
                    "sequence": seq,
                    "student_id": i.student_id.id if i.student_id else False,
                    "student_name": i.student_id.english_name if i.student_id.english_name else False,
                    "request_date": i.request_date if i.request_date else False,
                    "value": i.value if i.value else False,
                    "teachers_name": i.teachers_name if i.teachers_name else False,
                    "class_id": i.class_id.id if i.class_id else False,
                    "class_name": i.class_id.class_name if i.class_id else False,
                    "class_no":  i.class_no if i.class_no else False,
                    "receive_date":  i.receive_date if i.receive_date else False,
                    "redeem_type":  i.redeem_type if i.redeem_type else "",
                    "remarks": i.remarks if i.remarks else False,
                    "item_id": i.item_id.id if i.item_id else False,
                    "item_name": i.item_id.item_name if i.item_id.item_name else False,
                    "status": i.status if i.status else False,
                    "created_date": str(i.created_date),
                    "updated_date": str(i.updated_date)
                }
                redeem_records.append(redeem_vals)
                seq = seq + 1

            result_page = paginator.paginate_queryset(redeem_records, request)
            paginator_data = paginator.get_paginated_response(result_page).data
            if len(redeem_records) > 0:
                paginator_data['total_pages'] = math.ceil(len(redeem_records) / page_size)
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


class RedeemRecordFormAPI(generics.ListCreateAPIView):
    """
        Redeem item Form
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = RedeemRecordsSerializer
    queryset = RedeemRecord.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Get Redeem Item
            :param request: Id
            :param kwargs: NA
            :return: Redeem Record
        """
        if not request.user.student_id:
            if request.user.role_id is None:
                return Response({"success": False, "message": "User has no role id set"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not (request.user.role_id.all_privileges or request.user.role_id.redeem_item_record):
                return Response({"success": False, "message": "User has no privilege to redeem item record"},
                                status=status.HTTP_400_BAD_REQUEST)

        redeem_record_id = request.data.get('id')

        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        snippets = self.queryset.filter(id=redeem_record_id).first()

        if snippets:
            i = snippets
            redeem_vals = {
                "id": i.id if i.id else False,
                "student_id": i.student_id.id if i.student_id else False,
                "student_name": i.student_id.english_name if i.student_id.english_name else False,
                "request_date": i.request_date if i.request_date else False,
                "value": i.value if i.value else False,
                "teachers_name": i.teachers_name if i.teachers_name else False,
                "class_id": i.class_id.id if i.class_id else False,
                "class_name": i.class_id.class_name if i.class_id else False,
                "class_no": i.class_no if i.class_no else False,
                "receive_date": i.receive_date if i.receive_date else False,
                "redeem_type": i.redeem_type if i.redeem_type else "",
                "remarks": i.remarks if i.remarks else False,
                "item_id": i.item_id.id if i.item_id else False,
                "item_name": i.item_id.item_name if i.item_id.item_name else False,
                "status": i.status if i.status else False,
                "created_date": str(i.created_date),
                "updated_date": str(i.updated_date)
            }
            return Response({
                "success": True,
                "message": "Success",
                "data": redeem_vals,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class StudentRedeemList(generics.ListCreateAPIView):
    """
        Get Student Service List
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = RedeemSerializer
    queryset = Redeem.objects.all().order_by('id')

    def post(self, request, *args, **kwargs):
        """
            Get all Redeem Filter
            :param request: Redeem Records
            :param kwargs: NA
            :return: Redeem Records
        """

        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        paginator = RedeemPagination()
        page_size = paginator.page_size

        snippets = self.queryset.all()
        regular_list = []
        special_list = []
        seq = 1
        if snippets:
            for i in snippets:
                if i.redeem_type == "regular":
                    redeem_vals = {
                        "id": i.id if i.id else False,
                        "sequence": seq,
                        "item_name": i.item_name if i.item_name else False,
                        "rubies": i.rubies if i.rubies else False,
                        "wamfo_coins": i.value if i.value else False,
                        "amount": i.amount if i.amount else False,
                        "teachers_name": i.teachers_name if i.teachers_name else False,
                        "icon":  urls + "/media/" + str(i.icon) if i.icon else "",
                        "status": i.status if i.status else False,
                        "redeem_type": i.redeem_type if i.redeem_type else "",
                        "created_date": str(i.created_date),
                        "updated_date": str(i.updated_date)
                    }
                    regular_list.append(redeem_vals)
                seq = seq + 1
                if i.redeem_type == "special":
                    redeem_vals = {
                        "id": i.id if i.id else False,
                        "sequence": seq,
                        "item_name": i.item_name if i.item_name else False,
                        "rubies": i.rubies if i.rubies else False,
                        "wamfo_coins": i.value if i.value else False,
                        "amount": i.amount if i.amount else False,
                        "teachers_name": i.teachers_name if i.teachers_name else False,
                        "icon":  urls + "/media/" + str(i.icon) if i.icon else "",
                        "status": i.status if i.status else False,
                        "redeem_type": i.redeem_type if i.redeem_type else "",
                        "created_date": str(i.created_date),
                        "updated_date": str(i.updated_date)
                    }
                    special_list.append(redeem_vals)
                seq = seq + 1
            redeem_data = {
                "regular": regular_list,
                "special": special_list
            }

            return Response({
                "success": True,
                "message": "Success",
                "data": redeem_data,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class StudentRedeemApplyRegular(generics.ListCreateAPIView):
    """
        Get Character List
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = RedeemSerializer
    queryset = Redeem.objects.all().order_by('id')

    def post(self, request, *args, **kwargs):
        """
            Get all Characters
            :param request: Service Records
            :param kwargs: NA
            :return: all Characters
        """

        user_id = request.data.get('user_id')
        redeem_item_id = request.data.get('redeem_item_id')

        if user_id and redeem_item_id:
            user_data = User.objects.filter(id=user_id).first()
            redeem_value = Redeem.objects.filter(id=redeem_item_id, redeem_type="regular").first()
            if user_data and redeem_value:
                if user_data.login_points >= redeem_value.value:
                    new_wamfo_coin = user_data.login_points - redeem_value.value
                    new_rubies = user_data.student_rubies + redeem_value.rubies
                    user_data.login_points = new_wamfo_coin
                    user_data.student_rubies = new_rubies
                    user_data.save()
                    class_data = False
                    if user_data.class_id:
                        class_data = Class.objects.filter(id=user_data.class_id.id).first()
                    if not class_data:
                        class_data = False

                    redeem_records = RedeemRecord.objects.create(item_id=redeem_value,
                                                                 value=redeem_value.value if redeem_value.value else "",
                                                                 student_id=user_data,
                                                                 teachers_name=redeem_value.teachers_name if redeem_value.teachers_name else "",
                                                                 class_no=user_data.class_no if user_data.class_no else "",
                                                                 class_id=class_data if class_data else None,
                                                                 )

                    return Response({
                        "success": True,
                        "message": "Rubies Updated",
                        "data": {},
                    }, status=status.HTTP_200_OK)

                else:
                    return Response({"success": False, "message": "Not Enough Wamfo Coins", "data": {}},
                                    status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({"success": False, "message": "Not Found", "data": {}},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class StudentRedeemApplySpecial(generics.ListCreateAPIView):
    """
        Get Character List
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = RedeemSerializer
    queryset = Redeem.objects.all().order_by('id')

    def post(self, request, *args, **kwargs):
        """
            Get all Characters
            :param request: Service Records
            :param kwargs: NA
            :return: all Characters
        """

        user_id = request.data.get('user_id')
        redeem_item_id = request.data.get('redeem_item_id')

        if user_id and redeem_item_id:
            user_data = User.objects.filter(id=user_id).first()
            redeem_value = Redeem.objects.filter(id=redeem_item_id, redeem_type="special").first()
            if user_data and redeem_value:
                if user_data.student_rubies >= redeem_value.rubies:
                    # new_wamfo_coin = user_data.login_points - redeem_value.value
                    # new_rubies = user_data.student_rubies + redeem_value.rubies
                    # user_data.login_points = new_wamfo_coin
                    # user_data.student_rubies = new_rubies
                    # user_data.save()
                    class_data = False
                    if user_data.class_id:
                        class_data = Class.objects.filter(id=user_data.class_id.id).first()
                    if not class_data:
                        class_data = False

                    redeem_records = RedeemRecord.objects.create(item_id=redeem_value,
                                                                 value=redeem_value.value if redeem_value.value else "",
                                                                 student_id=user_data,
                                                                 teachers_name=redeem_value.teachers_name if redeem_value.teachers_name else "",
                                                                 class_no=user_data.class_no if user_data.class_no else "",
                                                                 class_id=class_data if class_data else None,
                                                                 )
                    return Response({
                        "success": True,
                        "message": "Request Updated",
                        "data": {},
                    }, status=status.HTTP_200_OK)

                else:
                    return Response({"success": False, "message": "Not Enough Wamfo Coins", "data": {}},
                                    status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({"success": False, "message": "Not Found", "data": {}},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class RedeemItemsAPI(generics.ListCreateAPIView):
    """
        Redeem create
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = RedeemSerializer
    queryset = Redeem.objects.all().order_by('id')

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
        if not request.user.student_id:
            if request.user.role_id is None:
                return Response({"success": False, "message": "User has no role id set"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not (request.user.role_id.all_privileges or (
                    request.user.role_id.redeemed_items and request.user.role_id.redeem_item_list and request.user.role_id.redeem_item_record)):
                return Response({"success": False, "message": "User has no privilege to redeem item list"},
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


class RedeemItemsListAPI(generics.ListCreateAPIView):
    """
        Redeem item List
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = RedeemSerializer
    queryset = Redeem.objects.all().order_by('id')

    def get(self, request, *args, **kwargs):
        """
            Get all Redeem Filter
            :param request: Redeem Records
            :param kwargs: NA
            :return: Redeem Records
        """
        if not request.user.student_id:
            if request.user.role_id is None:
                return Response({"success": False, "message": "User has no role id set"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not (request.user.role_id.all_privileges or request.user.role_id.redeem_item_list):
                return Response({"success": False, "message": "User has no privilege to redeem item list"},
                                status=status.HTTP_400_BAD_REQUEST)

        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        paginator = RedeemPagination()
        page_size = paginator.page_size

        snippets = self.queryset.all()
        regular_list = []
        special_list = []
        seq = 1

        if snippets:
            for i in snippets:
                if i.redeem_type == "regular":
                    redeem_vals = {
                        "id": i.id if i.id else False,
                        "sequence": seq,
                        "item_name": i.item_name if i.item_name else False,
                        "rubies": i.rubies if i.rubies else False,
                        "introduction": i.introduction if i.introduction else "",
                        "stock": i.stock if i.stock else False,
                        "teachers_name": i.teachers_name if i.teachers_name else False,
                        "icon": urls + "/media/" + str(i.icon) if i.icon else "",
                        "status": i.status if i.status else False,
                        "redeem_type": i.redeem_type if i.redeem_type else "",
                        "created_date": str(i.created_date),
                        "updated_date": str(i.updated_date)
                    }
                    regular_list.append(redeem_vals)
                seq = seq + 1
                if i.redeem_type == "special":
                    redeem_vals = {
                        "id": i.id if i.id else False,
                        "sequence": seq,
                        "item_name": i.item_name if i.item_name else False,
                        "rubies": i.rubies if i.rubies else False,
                        "introduction": i.introduction if i.introduction else "",
                        "stock": i.stock if i.stock else False,
                        "teachers_name": i.teachers_name if i.teachers_name else False,
                        "icon": urls + "/media/" + str(i.icon) if i.icon else "",
                        "status": i.status if i.status else False,
                        "redeem_type": i.redeem_type if i.redeem_type else "",
                        "created_date": str(i.created_date),
                        "updated_date": str(i.updated_date)
                    }
                    special_list.append(redeem_vals)
                seq = seq + 1
            redeem_data = {
                "regular": regular_list,
                "special": special_list
            }

            return Response({
                "success": True,
                "message": "Success",
                "data": redeem_data,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class RedeemItemsFormAPI(generics.ListCreateAPIView):
    """
        Redeem item Form
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = RedeemSerializer
    queryset = Redeem.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Get Redeem Item
            :param request: Id
            :param kwargs: NA
            :return: Redeem Record
        """
        if not request.user.student_id:
            if request.user.role_id is None:
                return Response({"success": False, "message": "User has no role id set"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not (request.user.role_id.all_privileges or request.user.role_id.redeem_item_list):
                return Response({"success": False, "message": "User has no privilege to redeem item form"},
                                status=status.HTTP_400_BAD_REQUEST)
        redeem_id = request.data.get('id')

        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        snippets = self.queryset.filter(id=redeem_id).first()

        if snippets:
            i = snippets
            redeem_vals = {
                "id": i.id if i.id else False,
                "item_name": i.item_name if i.item_name else False,
                "rubies": i.rubies if i.rubies else False,
                "introduction": i.introduction if i.introduction else "",
                "stock": i.stock if i.stock else False,
                "teachers_name": i.teachers_name if i.teachers_name else False,
                "icon": urls + "/media/" + str(i.icon) if i.icon else False,
                "status": i.status if i.status else False,
                "redeem_type": i.redeem_type if i.redeem_type else "",
                "created_date": str(i.created_date),
                "updated_date": str(i.updated_date)
            }
            return Response({
                "success": True,
                "message": "Success",
                "data": redeem_vals,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class RedeemItem(generics.GenericAPIView):
    serializer_class = RedeemRecordsSerializer

    def post(self, request):
        user_id = request.data.get('user_id')
        redeem_id = request.data.get('redeem_id')
        user_obj = User.objects.get(id=user_id)
        redeem_obj = Redeem.objects.get(id=redeem_id)
        if not user_obj.student_rubies >= redeem_obj.rubies:
            return Response({"success": False, "message": "Not Enough Rubies to redeem"},
                            status=status.HTTP_400_BAD_REQUEST)
        if redeem_obj.stock is None or redeem_obj.stock <= 0:
            redeem_obj.status = False
            redeem_obj.save()
            return Response({"success": False, "message": "Not Enough stock to redeem"},
                            status=status.HTTP_400_BAD_REQUEST)

        context = {
            'item_id': redeem_obj.id,
            'teachers_name': redeem_obj.teachers_name,
            'student_id': user_obj.id,
            'class_id': user_obj.class_id.id,
            'class_no': user_obj.class_no,
            'redeem_type': redeem_obj.redeem_type,
        }
        serializer = self.serializer_class(data=context)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Success",
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED)
        return Response({"success": False, "message": "Failed", "data": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class RegularRedeemItem(generics.GenericAPIView):

    def post(self, request):
        user_id = request.data.get('user_id')
        coins = request.data.get('coins')
        rubies = request.data.get('rubies')
        user_obj = User.objects.get(id=user_id)
        ruby = rubies
        coin = ruby * 100
        if coin == coins:
            if user_obj.login_points >= coins:
                user_obj.login_points = user_obj.login_points - coins
                user_obj.student_rubies = user_obj.student_rubies + rubies
                user_obj.save()
                return Response({"success": True, "message": "Success"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"success": False, "message": "Failed"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"success": False, "message": "Failed"}, status=status.HTTP_400_BAD_REQUEST)

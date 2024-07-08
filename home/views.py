from rest_framework import status, generics
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.response import Response
from accounts . serializers import CharacterOwnedSerializer, CharacterToolSerializer, CharacterArmorSerializer
from .serializers import RecoverVitalitySerializer
from .models import RecoverVitality
from accounts.models import User
from rest_framework.permissions import IsAuthenticated
from .pagination import HomePagination
import math
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404


class RecoverVitalityAPI(generics.ListCreateAPIView):
    """
        List and Create Characters
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = RecoverVitalitySerializer
    queryset = RecoverVitality.objects.all().order_by('id')

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
            create Characters
            :param request: Characters
            :param kwargs: NA
            :return: Characters details
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


class RecoverVitalityAPIList(generics.ListCreateAPIView):
    """
        Get Character List
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = RecoverVitalitySerializer
    queryset = RecoverVitality.objects.all().order_by('id')

    def post(self, request, *args, **kwargs):
        """
            Get all Characters
            :param request: Service Records
            :param kwargs: NA
            :return: all Characters
        """

        user_id = request.data.get('user_id')
        recover_vitality_id = request.data.get('recover_vitality_id')

        if user_id and recover_vitality_id:
            user_data = User.objects.filter(id=user_id).first()
            recover_vitality = RecoverVitality.objects.filter(id=recover_vitality_id).first()
            if user_data and recover_vitality:
                if user_data.login_points >= recover_vitality.wamfo_coins:
                    new_wamfo_coin = user_data.login_points - recover_vitality.wamfo_coins
                    new_vitality = user_data.student_vitality + recover_vitality.vitality
                    user_data.login_points = new_wamfo_coin
                    user_data.student_vitality = new_vitality
                    user_data.save()
                    return Response({
                        "success": True,
                        "message": "Vitality Updated",
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


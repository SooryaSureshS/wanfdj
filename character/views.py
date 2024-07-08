from rest_framework import status, generics
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.response import Response
from accounts . serializers import CharacterOwnedSerializer, CharacterToolSerializer, CharacterArmorSerializer
from .serializers import CharacterSerializer, ArmorSerializer, ToolSerializer
from .models import Character, Armor, Tool
from accounts.models import User, CharacterOwned, CharacterTool, CharacterArmor
from rest_framework.permissions import IsAuthenticated
from .pagination import CharacterPagination
import math
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404


class Characters(generics.ListCreateAPIView):
    """
        List and Create Characters
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = CharacterSerializer
    queryset = Character.objects.all().order_by('id')

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


class CharactersList(generics.ListCreateAPIView):
    """
        Get Character List
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = CharacterSerializer
    queryset = Character.objects.all().order_by('id')

    def post(self, request, *args, **kwargs):
        """
            Get all Characters
            :param request: Service Records
            :param kwargs: NA
            :return: all Characters
        """

        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        paginator = CharacterPagination()
        page_size = paginator.page_size

        snippets = self.queryset.all()
        character_records = []
        seq = 1
        if snippets:
            for i in snippets:
                character_vals = {
                    "id": i.id if i.id else False,
                    "sequence": seq,
                    "name": i.name if i.name else False,
                    "character_image": urls + "/media/" + str(
                        i.character_image) if i.character_image else False,
                    "created_date": str(i.created_date),
                    "updated_date": str(i.updated_date)
                }
                character_records.append(character_vals)
                seq = seq + 1
            sorted_character_records = sorted(character_records, key=lambda x: x['sequence'], reverse=True)

            result_page = paginator.paginate_queryset(sorted_character_records, request)
            paginator_data = paginator.get_paginated_response(result_page).data
            if len(sorted_character_records) > 0:
                paginator_data['total_pages'] = math.ceil(len(sorted_character_records) / page_size)
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


class CharactersForm(generics.ListCreateAPIView):
    """
        Get Single Service Record
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = CharacterSerializer
    queryset = Character.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Get Character Record
            :param request: Service Record id
            :param kwargs: NA
            :return: Specific Character Record
        """
        character_id = request.data.get('id')
        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        if character_id:
            snippets = self.queryset.filter(id=character_id)
            if snippets:
                for i in snippets:
                    character_vals = {
                        "id": i.id if i.id else False,
                        "name": i.name if i.name else False,
                        "character_image": urls + "/media/" + str(
                            i.character_image) if i.character_image else False,
                        "created_date": str(i.created_date),
                        "updated_date": str(i.updated_date)
                    }
                    return Response({
                        "success": True,
                        "message": "Success",
                        "data": character_vals,
                    }, status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "Not Found", "data": {}},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class Armors(generics.ListCreateAPIView):
    """
        List and Create Armors
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = ArmorSerializer
    queryset = Armor.objects.all().order_by('id')

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
            create Armors
            :param request: Armors Services
            :param kwargs: NA
            :return: Armors details
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


class ArmorsList(generics.ListCreateAPIView):
    """
        Get Character List
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ArmorSerializer
    queryset = Armor.objects.all().order_by('id')

    def post(self, request, *args, **kwargs):
        """
            Get all Armors
            :param request: Armor
            :param kwargs: NA
            :return: all Armors
        """

        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        paginator = CharacterPagination()
        page_size = paginator.page_size

        snippets = self.queryset.all()
        armor_records = []
        seq = 1
        if snippets:
            for i in snippets:
                armor_vals = {
                    "id": i.id if i.id else False,
                    "sequence": seq,
                    "name": i.name if i.name else False,
                    "armor_image": urls + "/media/" + str(
                        i.armor_image) if i.armor_image else False,
                    "created_date": str(i.created_date),
                    "updated_date": str(i.updated_date)
                }
                armor_records.append(armor_vals)
                seq = seq + 1
            sorted_character_records = sorted(armor_records, key=lambda x: x['sequence'], reverse=True)

            result_page = paginator.paginate_queryset(sorted_character_records, request)
            paginator_data = paginator.get_paginated_response(result_page).data
            if len(sorted_character_records) > 0:
                paginator_data['total_pages'] = math.ceil(len(sorted_character_records) / page_size)
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


class ArmorsForm(generics.ListCreateAPIView):
    """
        Get Single Service Record
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ArmorSerializer
    queryset = Armor.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Get Armor
            :param request: Armor id
            :param kwargs: NA
            :return: Specific Armor Record
        """
        armor_id = request.data.get('id')
        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        if armor_id:
            snippets = self.queryset.filter(id=armor_id)
            if snippets:
                for i in snippets:
                    armor_vals = {
                        "id": i.id if i.id else False,
                        "name": i.name if i.name else False,
                        "armor_image": urls + "/media/" + str(
                            i.armor_image) if i.armor_image else False,
                        "created_date": str(i.created_date),
                        "updated_date": str(i.updated_date)
                    }
                    return Response({
                        "success": True,
                        "message": "Success",
                        "data": armor_vals,
                    }, status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "Not Found", "data": {}},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class Tools(generics.ListCreateAPIView):
    """
        List and Create Armors
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = ToolSerializer
    queryset = Tool.objects.all().order_by('id')

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
            create Tools
            :param request: Tools
            :param kwargs: NA
            :return: Tools details
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


class ToolsList(generics.ListCreateAPIView):
    """
        Get Character List
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ToolSerializer
    queryset = Tool.objects.all().order_by('id')

    def post(self, request, *args, **kwargs):
        """
            Get all Tools
            :param request: Tools
            :param kwargs: NA
            :return: all Tools
        """

        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        paginator = CharacterPagination()
        page_size = paginator.page_size

        snippets = self.queryset.all()
        tool_records = []
        seq = 1
        if snippets:
            for i in snippets:
                tool_vals = {
                    "id": i.id if i.id else False,
                    "sequence": seq,
                    "name": i.name if i.name else False,
                    "tool_image": urls + "/media/" + str(
                        i.tool_image) if i.tool_image else False,
                    "created_date": str(i.created_date),
                    "updated_date": str(i.updated_date)
                }
                tool_records.append(tool_vals)
                seq = seq + 1
            sorted_character_records = sorted(tool_records, key=lambda x: x['sequence'], reverse=True)

            result_page = paginator.paginate_queryset(sorted_character_records, request)
            paginator_data = paginator.get_paginated_response(result_page).data
            if len(sorted_character_records) > 0:
                paginator_data['total_pages'] = math.ceil(len(sorted_character_records) / page_size)
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


class ToolsForm(generics.ListCreateAPIView):
    """
        Get Single Service Record
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ToolSerializer
    queryset = Tool.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Get Armor
            :param request: Tool id
            :param kwargs: NA
            :return: Specific Tool Record
        """
        tool_id = request.data.get('id')
        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        if tool_id:
            snippets = self.queryset.filter(id=tool_id)
            if snippets:
                for i in snippets:
                    armor_vals = {
                        "id": i.id if i.id else False,
                        "name": i.name if i.name else False,
                        "tool_image": urls + "/media/" + str(
                            i.tool_image) if i.tool_image else False,
                        "created_date": str(i.created_date),
                        "updated_date": str(i.updated_date)
                    }
                    return Response({
                        "success": True,
                        "message": "Success",
                        "data": armor_vals,
                    }, status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "Not Found", "data": {}},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


# Student APIS

class OwnedCharacter(generics.ListCreateAPIView):
    """
        All Owned Character
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ToolSerializer
    queryset = CharacterOwned.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Get User Owned Characters
            :param request: User Id
            :param kwargs: NA
            :return: User Owned Characters
        """
        user_id = request.data.get('user_id')
        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)
        owned_characters = []
        if user_id:
            snippets = self.queryset.filter(user_id=user_id)
            if snippets:
                for i in snippets:
                    owned_vals = {
                        "id": i.id if i.id else False,
                        "user_id": i.user_id.id if i.user_id else False,
                        "character_id": i.character_id.id if i.character_id else False,
                        "character_name": i.character_id.name if i.character_id else False,
                        "character_type": i.character_id.character_type if i.character_id else False,
                        "character_level": i.character_level if i.character_level else False,
                        "character_hp": i.character_hp if i.character_hp else False,
                        "dodge": i.dodge if i.dodge else False,
                        "critical": i.critical if i.critical else False,
                        "active": i.active if i.active else False,
                        "character_image": urls + "/media/" + str(
                            i.character_id.character_image) if i.character_id else False,
                        "created_date": str(i.created_date),
                        "updated_date": str(i.updated_date)
                    }
                    owned_characters.append(owned_vals)
                    return Response({
                        "success": True,
                        "message": "Success",
                        "data": owned_characters,
                    }, status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "Not Found", "data": {}},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class StudentAllCharacters(generics.ListCreateAPIView):
    """
        All Owned Character
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ToolSerializer
    queryset = CharacterOwned.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Get User Owned Characters by Group
            :param request: User Id
            :param kwargs: NA
            :return: User Owned Characters by Group
        """
        user_id = request.data.get('user_id')
        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        if user_id:
            snippets = self.queryset.filter(user_id=user_id)
            if snippets:
                normal = []
                rare = []
                super_rare = []
                epic = []
                legendary = []
                for i in snippets:
                    if i.character_id and i.character_id.character_type == 'normal':
                        normal_vals = {
                            "id": i.id if i.id else False,
                            "user_id": i.user_id.id if i.user_id else False,
                            "character_id": i.character_id.id if i.character_id else False,
                            "character_name": i.character_id.name if i.character_id else False,
                            "character_type": i.character_id.character_type if i.character_id else False,
                            "character_level": i.character_level if i.character_level else False,
                            "character_hp": i.character_hp if i.character_hp else False,
                            "dodge": i.dodge if i.dodge else False,
                            "critical": i.critical if i.critical else False,
                            "active": i.active if i.active else False,
                            "character_image": urls + "/media/" + str(
                                i.character_id.character_image) if i.character_id else False,
                            "created_date": str(i.created_date),
                            "updated_date": str(i.updated_date)
                        }
                        normal.append(normal_vals)
                    if i.character_id and i.character_id.character_type == 'rare':
                        rare_vals = {
                            "id": i.id if i.id else False,
                            "user_id": i.user_id.id if i.user_id else False,
                            "character_id": i.character_id.id if i.character_id else False,
                            "character_name": i.character_id.name if i.character_id else False,
                            "character_type": i.character_id.character_type if i.character_id else False,
                            "character_level": i.character_level if i.character_level else False,
                            "character_hp": i.character_hp if i.character_hp else False,
                            "dodge": i.dodge if i.dodge else False,
                            "critical": i.critical if i.critical else False,
                            "active": i.active if i.active else False,
                            "character_image": urls + "/media/" + str(
                                i.character_id.character_image) if i.character_id else False,
                            "created_date": str(i.created_date),
                            "updated_date": str(i.updated_date)
                        }
                        rare.append(rare_vals)
                    if i.character_id and i.character_id.character_type == 'super_rare':
                        super_rare_vals = {
                            "id": i.id if i.id else False,
                            "user_id": i.user_id.id if i.user_id else False,
                            "character_id": i.character_id.id if i.character_id else False,
                            "character_name": i.character_id.name if i.character_id else False,
                            "character_type": i.character_id.character_type if i.character_id else False,
                            "character_level": i.character_level if i.character_level else False,
                            "character_hp": i.character_hp if i.character_hp else False,
                            "dodge": i.dodge if i.dodge else False,
                            "critical": i.critical if i.critical else False,
                            "active": i.active if i.active else False,
                            "character_image": urls + "/media/" + str(
                                i.character_id.character_image) if i.character_id else False,
                            "created_date": str(i.created_date),
                            "updated_date": str(i.updated_date)
                        }
                        super_rare.append(super_rare_vals)
                    if i.character_id and i.character_id.character_type == 'epic':
                        epic_vals = {
                            "id": i.id if i.id else False,
                            "user_id": i.user_id.id if i.user_id else False,
                            "character_id": i.character_id.id if i.character_id else False,
                            "character_name": i.character_id.name if i.character_id else False,
                            "character_type": i.character_id.character_type if i.character_id else False,
                            "character_level": i.character_level if i.character_level else False,
                            "character_hp": i.character_hp if i.character_hp else False,
                            "dodge": i.dodge if i.dodge else False,
                            "critical": i.critical if i.critical else False,
                            "active": i.active if i.active else False,
                            "character_image": urls + "/media/" + str(
                                i.character_id.character_image) if i.character_id else False,
                            "created_date": str(i.created_date),
                            "updated_date": str(i.updated_date)
                        }
                        epic.append(epic_vals)
                    if i.character_id and i.character_id.character_type == 'legendary':
                        legendary_vals = {
                            "id": i.id if i.id else False,
                            "user_id": i.user_id.id if i.user_id else False,
                            "character_id": i.character_id.id if i.character_id else False,
                            "character_name": i.character_id.name if i.character_id else False,
                            "character_type": i.character_id.character_type if i.character_id else False,
                            "character_level": i.character_level if i.character_level else False,
                            "character_hp": i.character_hp if i.character_hp else False,
                            "dodge": i.dodge if i.dodge else False,
                            "critical": i.critical if i.critical else False,
                            "active": i.active if i.active else False,
                            "character_image": urls + "/media/" + str(
                                i.character_id.character_image) if i.character_id else False,
                            "created_date": str(i.created_date),
                            "updated_date": str(i.updated_date)
                        }
                        legendary.append(legendary_vals)
                all_characters = {
                    "normal": normal,
                    "rare": rare,
                    "super_rare": super_rare,
                    "epic": epic,
                    "legendary": legendary
                }
                return Response({
                    "success": True,
                    "message": "Success",
                    "data": all_characters,
                }, status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "Not Found", "data": {}},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class NotOwnedCharacter(generics.ListCreateAPIView):
    """
        All Not Owned Character
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ToolSerializer
    queryset = CharacterOwned.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Get Not Owned Characters
            :param request: User Id
            :param kwargs: NA
            :return: User Not Owned Characters
        """
        user_id = request.data.get('user_id')
        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)
        owned_characters = []
        if user_id:
            snippets = self.queryset.filter(user_id != user_id)
            if snippets:
                for i in snippets:
                    owned_vals = {
                        "id": i.id if i.id else False,
                        "user_id": i.user_id.id if i.user_id else False,
                        "character_id": i.character_id.id if i.character_id else False,
                        "character_name": i.character_id.name if i.character_id else False,
                        "character_type": i.character_id.character_type if i.character_id else False,
                        "active": i.active if i.active else False,
                        "character_image": urls + "/media/" + str(
                            i.character_id.character_image) if i.character_id else False,
                        "created_date": str(i.created_date),
                        "updated_date": str(i.updated_date)
                    }
                    owned_characters.append(owned_vals)
                    return Response({
                        "success": True,
                        "message": "Success",
                        "data": owned_characters,
                    }, status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "Not Found", "data": {}},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class CurrentCharacter(generics.ListCreateAPIView):
    """
        Get Single Character Record
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ToolSerializer
    queryset = CharacterOwned.objects.all().order_by('-id')

    def post(self, request, *args, **kwargs):
        """
            Get Armor
            :param request: Tool id
            :param kwargs: NA
            :return: Specific Tool Record
        """
        user_id = request.data.get('user_id')
        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        if user_id:
            snippets = self.queryset.filter(user_id=user_id, active=True)

            if snippets:
                for i in snippets:
                    selected_vals = {
                        "id": i.id if i.id else False,
                        "user_id": i.user_id.id if i.user_id else False,
                        "character_id": i.character_id.id if i.character_id else False,
                        "character_name": i.character_id.name if i.character_id else False,
                        "character_type": i.character_id.character_type if i.character_id else False,
                        "character_level": i.character_level if i.character_level else False,
                        "character_hp": i.character_hp if i.character_hp else False,
                        "dodge": i.dodge if i.dodge else False,
                        "critical": i.critical if i.critical else False,
                        "active": i.active if i.active else False,
                        "character_image": urls + "/media/" + str(
                            i.character_id.character_image) if i.character_id else False,
                        "created_date": str(i.created_date),
                        "updated_date": str(i.updated_date)
                    }
                    return Response({
                        "success": True,
                        "message": "Success",
                        "data": selected_vals,
                    }, status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "Not Found", "data": {}},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class StudentCharacterTool(generics.ListCreateAPIView):
    """
        Get Single Character Record
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = CharacterToolSerializer
    queryset = CharacterTool.objects.all().order_by('id')

    def post(self, request, *args, **kwargs):
        """
            Get Armor
            :param request: Tool id
            :param kwargs: NA
            :return: Specific Tool Record
        """
        user_id = request.data.get('user_id')
        owned_character_id = request.data.get('owned_character_id')
        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        if user_id and owned_character_id:
            snippets = self.queryset.all()
            if snippets:
                tool_list = []
                for i in snippets:
                    if str(i.owned_character_id.user_id.id) == str(user_id) and str(i.owned_character_id.id) == str(owned_character_id):
                        tool_vals = {
                            "id": i.id if i.id else False,
                            "user_id": i.owned_character_id.user_id.id if i.owned_character_id.user_id else False,
                            "tool_id": i.tool_id.id if i.tool_id else False,
                            "tool_name": i.tool_id.id if i.tool_id else False,
                            "character_id": i.owned_character_id.id if i.owned_character_id else False,
                            "character_name": i.owned_character_id.character_id.name if i.owned_character_id.character_id else False,
                            "character_type": i.owned_character_id.character_id.character_type if i.owned_character_id.character_id else False,
                            "active": i.active if i.active else False,
                            "created_date": str(i.created_date),
                            "updated_date": str(i.updated_date)
                        }
                        tool_list.append(tool_vals)

                return Response({
                    "success": True,
                    "message": "Success",
                    "data": tool_list,
                }, status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "Not Found", "data": {}},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


class StudentCharacterArmor(generics.ListCreateAPIView):
    """
        Get Single Character Record
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = CharacterArmorSerializer
    queryset = CharacterArmor.objects.all().order_by('id')

    def post(self, request, *args, **kwargs):
        """
            Get Armor
            :param request: Tool id
            :param kwargs: NA
            :return: Specific Tool Record
        """
        user_id = request.data.get('user_id')
        owned_character_id = request.data.get('owned_character_id')
        http_layer = request.is_secure() and "https" or "http"
        http_address = request.get_host()
        urls = str(http_layer + "://" + http_address)

        if user_id and owned_character_id:
            snippets = self.queryset.all()
            if snippets:
                armor_list = []
                for i in snippets:
                    if str(i.owned_character_id.user_id.id) == str(user_id) and str(i.owned_character_id.id) == str(owned_character_id):
                        armor_vals = {
                            "id": i.id if i.id else False,
                            "user_id": i.owned_character_id.user_id.id if i.owned_character_id.user_id else False,
                            "armor_id": i.armor_id.id if i.armor_id else False,
                            "armor_name": i.armor_id.id if i.armor_id else False,
                            "character_id": i.owned_character_id.id if i.owned_character_id else False,
                            "character_name": i.owned_character_id.character_id.name if i.owned_character_id.character_id else False,
                            "character_type": i.owned_character_id.character_id.character_type if i.owned_character_id.character_id else False,
                            "active": i.active if i.active else False,
                            "created_date": str(i.created_date),
                            "updated_date": str(i.updated_date)
                        }
                        armor_list.append(armor_vals)

                return Response({
                    "success": True,
                    "message": "Success",
                    "data": armor_list,
                }, status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "Not Found", "data": {}},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"success": False, "message": "Not Found", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)


from rest_framework import serializers
from .models import Character, Armor, Tool


class CharacterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Character
        fields = '__all__'


class ArmorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Armor
        fields = '__all__'


class ToolSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tool
        fields = '__all__'

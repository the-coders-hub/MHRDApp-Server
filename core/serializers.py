from rest_framework import serializers
from .models import File, Tag
from django.contrib.auth.models import User
from account.serializers import FilteredDesignationSerializer


class FileSerializer(serializers.ModelSerializer):

    class Meta:
        model = File
        fields = ['file', 'mime_type']
        read_only_fields = ['mime_type']


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['tag']


class UserSerializer(serializers.ModelSerializer):
    picture = FileSerializer(source='profile.picture')
    designations = FilteredDesignationSerializer(many=True, source='profile.designations')

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'picture', 'designations']


class SimpleResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=False)
    message = serializers.CharField()


class LoginResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=False)
    token = serializers.UUIDField()


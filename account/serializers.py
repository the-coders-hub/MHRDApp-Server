from rest_framework import serializers
from .models import SignUpCode
from django.contrib.auth.models import User


class SignUpWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = SignUpCode
        fields = ['email']


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=8, min_length=8)
    username = serializers.CharField(max_length=32)
    password = serializers.CharField(max_length=32, min_length=8)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(max_length=32)
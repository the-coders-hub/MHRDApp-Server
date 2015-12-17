from rest_framework import serializers
from .models import SignUpCode, Designation, UserProfile


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


class FilteredVerifiedDesignation(serializers.ListSerializer):

    def to_representation(self, data):
        data = data.filter(verified=True)
        return super().to_representation(data)


class FilteredDesignationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Designation
        read_only_fields = ['id', 'verified']
        list_serializer_class = FilteredVerifiedDesignation


class DesignationSerializer(FilteredDesignationSerializer):

    class Meta:
        model = Designation


class UpdateProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'college']

    def update(self, instance, validated_data):
        user = instance.user
        try:
            user.first_name = validated_data['user']['first_name']
        except KeyError:
            pass
        try:
            user.last_name = validated_data['user']['last_name']
        except KeyError:
            pass
        user.save()
        instance.college = validated_data['college']
        instance.save()
        return instance

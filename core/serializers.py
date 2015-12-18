from rest_framework import serializers
from .models import File, Tag
from django.contrib.auth.models import User
from account.serializers import FilteredDesignationSerializer
import django.utils.six
import base64
import binascii
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as _


class Base64FileField(serializers.FileField):

    def to_internal_value(self, data):
        if not data:
            return None

        if isinstance(data, django.utils.six.string_types):
            try:
                decoded_data = base64.b64decode(data)
            except (TypeError, binascii.Error):
                raise ValidationError(_("Please upload a valid file"))

            file_data = ContentFile(decoded_data, 'uploadedfile.temp')
            return super().to_internal_value(file_data)
        raise ValidationError(_('Not a valid base64 string'))


class FileSerializer(serializers.ModelSerializer):
    file = Base64FileField()

    class Meta:
        model = File
        fields = ['file', 'mime_type']
        read_only_fields = ['mime_type']


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'tag']


class UserSerializer(serializers.ModelSerializer):
    picture = FileSerializer(source='profile.picture')
    college = serializers.SerializerMethodField()
    designations = FilteredDesignationSerializer(many=True, source='profile.designations')

    def get_college(self, obj):
        from college.serializers import CollegeSerializer
        return CollegeSerializer(obj.profile.college).data

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'college', 'picture', 'designations']


class SimpleResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=False)
    message = serializers.CharField()


class LoginResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=False)
    token = serializers.UUIDField()


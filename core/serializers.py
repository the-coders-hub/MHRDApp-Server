from rest_framework.serializers import ModelSerializer
from .models import File, Tag


class FileSerializer(ModelSerializer):

    class Meta:
        model = File
        fields = ['file', 'mime_type']


class TagSerializer(ModelSerializer):

    class Meta:
        model = Tag
        fields = ['tag']
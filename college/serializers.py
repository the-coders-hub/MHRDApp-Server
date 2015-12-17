from rest_framework import serializers
from core.serializers import FileSerializer, TagSerializer
from .models import College


class CollegeSerializer(serializers.ModelSerializer):
    logo = FileSerializer()
    cover = FileSerializer()
    tags = serializers.StringRelatedField(many=True)

    class Meta:
        model = College
        exclude_fields = ['email_domains']

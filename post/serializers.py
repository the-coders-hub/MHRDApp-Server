from rest_framework import serializers
from .models import Post, Reply
from core.serializers import FileSerializer, UserSerializer


class PostSerializer(serializers.ModelSerializer):
    attachments = FileSerializer(many=True)
    user = UserSerializer()
    tags = serializers.StringRelatedField(many=True)
    upvotes = serializers.IntegerField(source='upvotes.count')
    downvotes = serializers.IntegerField(source='downvotes.count')

    @classmethod
    def get_user(cls, obj):
        if obj.anonymous:
            return None
        return UserSerializer(obj.user).data

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'created', 'tags', 'anonymous', 'visibility', 'attachments'
                  'upvotes', 'downvotes', 'user']


class NewPostSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True)

    class Meta:
        model = Post
        fields = ['title', 'content', 'tags', 'anonymous', 'visibility']

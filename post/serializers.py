from rest_framework import serializers
from .models import Post, Reply
from core.serializers import FileSerializer, UserSerializer
from core.models import Tag


class PostSerializer(serializers.ModelSerializer):
    attachments = FileSerializer(many=True)
    user = UserSerializer()
    tags = serializers.StringRelatedField(many=True, required=False)
    upvotes = serializers.IntegerField(source='upvotes.count')
    downvotes = serializers.IntegerField(source='downvotes.count')

    @classmethod
    def get_user(cls, obj):
        if obj.anonymous:
            return None
        return UserSerializer(obj.user).data

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'created', 'tags', 'anonymous', 'visibility', 'attachments',
                  'upvotes', 'downvotes', 'user']


class NewPostSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), required=False)
    attachments = FileSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = ['title', 'content', 'tags', 'anonymous', 'visibility', 'attachments']


class UpdatePostSerializer(NewPostSerializer):
    title = serializers.CharField(max_length=256, required=False)
    content = serializers.CharField(required=False)

    class Meta(NewPostSerializer.Meta):
        fields = ['title', 'content', 'tags', 'anonymous', 'visibility']


class ReplySerializer(serializers.ModelSerializer):
    upvotes = serializers.IntegerField(source='upvotes.count')
    downvotes = serializers.IntegerField(source='downvotes.count')

    class Meta:
        model = Reply

class NewReplySerializer(serializers.ModelSerializer):
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Reply
        fields = ['post', 'content', 'visibility']
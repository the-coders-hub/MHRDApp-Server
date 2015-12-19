from rest_framework import serializers
from .models import Post, Reply
from core.serializers import FileSerializer, UserSerializer
from core.models import Tag


class PostSerializer(serializers.ModelSerializer):
    attachments = FileSerializer(many=True)
    user = serializers.SerializerMethodField()
    tags = serializers.StringRelatedField(many=True, required=False)
    upvotes = serializers.IntegerField(source='upvotes.count')
    downvotes = serializers.IntegerField(source='downvotes.count')
    user_vote = serializers.SerializerMethodField()

    def get_user_vote(self, obj):
        try:
            user = self.context['request'].user
        except KeyError:
            return 0
        if user in obj.upvotes.all():
            return 1
        if user in obj.downvotes.all():
            return -1
        return 0

    def get_user(self, obj):
        try:
            user = self.context['request'].user
        except KeyError:
            user = None
        if user == obj.user or not obj.anonymous:
            return UserSerializer(obj.user).data
        return None

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'created', 'tags', 'anonymous', 'visibility', 'attachments',
                  'upvotes', 'downvotes', 'user', 'user_vote']


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
    user = UserSerializer()
    user_vote = serializers.SerializerMethodField()

    def get_user_vote(self, obj):
        try:
            user = self.context['request'].user
        except KeyError:
            return 0
        if user in obj.upvotes.all():
            return 1
        if user in obj.downvotes.all():
            return -1
        return 0

    class Meta:
        model = Reply

class NewReplySerializer(serializers.ModelSerializer):
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Reply
        fields = ['post', 'content', 'visibility']
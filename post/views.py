from rest_framework import viewsets
from .serializers import PostSerializer, NewPostSerializer, UpdatePostSerializer, ReplySerializer, NewReplySerializer
from .models import Post, Reply, CONTENT_VISIBLE, CONTENT_DELETED, CONTENT_HIDDEN
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
from core.models import File
from django.http import Http404
from core.views import SerializerClassRequestContextMixin


class PostViewset(SerializerClassRequestContextMixin, viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base_queryset = Post.objects.all()
        queryset = base_queryset.filter(visibility=CONTENT_VISIBLE)
        queryset |= base_queryset.filter(visibility=CONTENT_HIDDEN, user=user)
        queryset = queryset.order_by('-created')
        return queryset

    def create(self, request, *args, **kwargs):
        """
        Create new Post
        ---
        response_serializer: post.serializers.PostSerializer
        parameters:
          - name: body
            pytype: post.serializers.NewPostSerializer
            paramType: body
        parameters_strategy:
            form: replace

        """
        serialized_data = NewPostSerializer(data=request.data)
        if serialized_data.is_valid():
            attachments = serialized_data.validated_data.get('attachments', [])
            files = []
            for attachment in attachments:
                file = File.objects.create(file=attachment['file'])
                files.append(file)

            post = Post.objects.create(
                title=serialized_data.validated_data['title'],
                content=serialized_data.validated_data['content'],
                user=request.user,
            )
            visibility = serialized_data.validated_data.get('visibility')
            anonymous = serialized_data.validated_data.get('anonymous')
            if visibility:
                post.visibility = visibility
            if anonymous:
                post.anonymous = anonymous

            post.save()
            tags = serialized_data.validated_data.get('tags', [])
            post.tags.add(*tags)
            post.attachments.add(*files)

            return Response(self.get_context_serializer_class(PostSerializer, post).data)
        else:
            return Response(serialized_data.errors, status=HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Update exisiting post. Only title, content, tags, anonymity and visibility can be updated.
        ---
        request_serializer: post.serializers.UpdatePostSerializer
        response_serializer: post.serializers.PostSerializer
        parameters:
          - name: body
            pytype: post.serializers.UpdatePostSerializer
            paramType: body
        parameters_strategy:
            form: replace
        """

        serialized_data = UpdatePostSerializer(data=request.data)
        post = self.get_object()
        if post.user.id != request.user.id:
            return Response({'success': False, 'message': 'Unauthorized access'}, status=HTTP_403_FORBIDDEN)

        if serialized_data.is_valid():

            try:
                post.title = serialized_data.validated_data['title']
            except KeyError:
                pass

            try:
                post.content = serialized_data.validated_data['content']
            except KeyError:
                pass

            try:
                tags = serialized_data.validated_data['tags']
                post.tags.clear()
                post.tags.add(*tags)
            except KeyError:
                pass

            try:
                post.anonymous = serialized_data.validated_data['anonymous']
            except KeyError:
                pass

            try:
                post.visibility = serialized_data.validated_data['visibility']
            except KeyError:
                pass

            post.save()
            return Response(self.get_context_serializer_class(PostSerializer, post).data)
        else:
            return Response(serialized_data.errors, status=HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        Delete post
        ---
        serializer: core.serializers.SimpleResponseSerializer
        """
        post = self.get_object()
        if post.user.id != request.user.id:
            return Response({'success': False, 'message': 'Unauthorized Access'}, status=HTTP_403_FORBIDDEN)

        for attachment in post.attachments.all():
            attachment.delete()

        post.visibility = CONTENT_DELETED
        post.save()
        return Response({'success': True, 'message': 'Post deleted'})

    def partial_update(self, request, *args, **kwargs):
        """
        Same as update. Don't know why this function is here.
        ---
        request_serializer: post.serializers.UpdatePostSerializer
        response_serializer: post.serializers.PostSerializer
        parameters:
          - name: body
            pytype: post.serializers.UpdatePostSerializer
            paramType: body
        parameters_strategy:
            form: replace
        """
        return self.update(request, *args, **kwargs)

    @detail_route(methods=['POST'])
    def upvote(self, request, pk):
        """
        Upvote a post. Remove downvote of user if present.
        ---
        parameters_strategy:
            form: replace

        """
        post = self.get_object()
        post.downvotes.remove(request.user)
        post.upvotes.add(request.user)
        return Response(self.get_context_serializer_class(PostSerializer, post).data)

    @detail_route(methods=['POST'])
    def downvote(self, request, pk):
        """
        Downvote a post. Remove upvote of user if present.
        ---
        parameters_strategy:
            form: replace
        """
        post = self.get_object()
        post.upvotes.remove(request.user)
        post.downvotes.add(request.user)
        return Response(self.get_context_serializer_class(PostSerializer, post).data)

    @detail_route(methods=['POST'])
    def remove_vote(self, request, pk):
        """
        Remove casted vote. Upvote -> remove_vote -> no vote.
        ---
        parameters_strategy:
            form: replace
        """
        post = self.get_object()
        post.upvotes.remove(request.user)
        post.downvotes.remove(request.user)
        return Response(self.get_context_serializer_class(PostSerializer, post).data)

    @detail_route()
    def get_replies(self, request, pk):
        """
        Get replies of a post. Include hidden replies only if user requesting is same as user posted
        ---
        serializer: post.serializers.ReplySerializer
        """
        post = self.get_object()
        if post.visibility in [CONTENT_HIDDEN, CONTENT_DELETED]:
            raise Http404
        replies = Reply.objects.all().filter(visibility=CONTENT_VISIBLE, post=post)
        replies |= Reply.objects.all().filter(visibility=CONTENT_HIDDEN, post=post, user=request.user)
        replies = replies.order_by('-created')
        return Response(self.get_context_serializer_class(ReplySerializer, replies, many=True).data)

    @list_route()
    def filtered(self, request):
        """
        Get posts related to user's college tags
        """
        college = request.user.profile.college
        if college:
            tags = college.tags.all()
        else:
            tags = []
        posts = self.get_queryset().filter(tags__in=tags).distinct()
        return Response(self.get_context_serializer_class(PostSerializer, posts, many=True).data)

    @list_route()
    def current(self, request):
        """
        Get posts of current user as OP
        """
        posts = self.get_queryset().filter(user=request.user)
        return Response(self.get_context_serializer_class(PostSerializer, posts, many=True).data)


class ReplyViewset(SerializerClassRequestContextMixin, viewsets.GenericViewSet):
    serializer_class = ReplySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        replies = Reply.objects.all().filter(visibility=CONTENT_VISIBLE)
        replies |= Reply.objects.all().filter(visibility=CONTENT_HIDDEN, user=self.request.user)
        return replies

    @list_route(methods=['POST'], serializer_class=NewReplySerializer)
    def add(self, request):
        """
        Create new reply.
        ---
        request_serializer: post.serializers.NewReplySerializer
        response_serializer: post.serializers.ReplySerializer
        """
        serialized_data = NewReplySerializer(data=request.data)
        if serialized_data.is_valid():
            reply = Reply(
                post=serialized_data.validated_data['post'],
                content=serialized_data.validated_data['content'],
                user=request.user
            )

            try:
                reply.visibility = serialized_data.validated_data['visibility']
            except KeyError:
                pass

            reply.save()
            return Response(self.get_context_serializer_class(ReplySerializer, reply).data)
        else:
            return Response(serialized_data.errors, status=HTTP_400_BAD_REQUEST)

    @detail_route(methods=['POST'])
    def delete(self, request, pk):
        """
        Delete a reply by id
        ---
        response_serializer: core.serializers.SimpleResponseSerializer
        parameters_strategy:
            form: replace
        """
        reply = self.get_object()
        if reply.user.id != request.user.id:
            return Response({'success': False, 'message': 'Unauthorized access'}, status=HTTP_403_FORBIDDEN)
        reply.visibility = CONTENT_DELETED
        reply.save()
        return Response({'success': True, 'message': 'Reply deleted successfully'})

    @detail_route(methods=['POST'])
    def upvote(self, request, pk):
        """
        Upvote a reply
        ---
        parameters_strategy:
            form: replace
        """
        reply = self.get_object()
        reply.downvotes.remove(request.user)
        reply.upvotes.add(request.user)
        return Response(self.get_context_serializer_class(ReplySerializer, reply).data)

    @detail_route(methods=['POST'])
    def downvote(self, request, pk):
        """
        Downvote a reply
        ---
        parameters_strategy:
            form: replace
        """
        reply = self.get_object()
        reply.upvotes.remove(request.user)
        reply.downvotes.add(request.user)
        return Response(self.get_context_serializer_class(ReplySerializer, reply).data)

    @detail_route(methods=['POST'])
    def remove_vote(self, request, pk):
        """
        Remove casted vote. Upvote -> remove_vote -> no vote.
        ---
        parameters_strategy:
            form: replace
        """
        reply = self.get_object()
        reply.upvotes.remove(request.user)
        reply.downvotes.remove(request.user)
        return Response(self.get_context_serializer_class(ReplySerializer, reply).data)

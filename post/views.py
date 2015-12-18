from rest_framework.viewsets import ModelViewSet
from .serializers import PostSerializer, NewPostSerializer, UpdatePostSerializer
from .models import Post, Reply, CONTENT_VISIBLE
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
from core.models import File


class PostViewset(ModelViewSet):
    queryset = Post.objects.all().filter(visibility=CONTENT_VISIBLE)
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

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
                post.anonymous = True

            post.save()
            post.tags.all().delete()
            tags = serialized_data.validated_data.get('tag', [])
            post.tags.add(*tags)
            post.attachments.all().delete()
            post.attachments.add(*files)

            return Response(PostSerializer(post).data)
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
                post.tags.all().delete()
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
            return Response(PostSerializer(post).data)
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

        for attachment in post.attachments:
            attachment.delete()

        post.delete()
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
        self.update(request, *args, **kwargs)

    @detail_route(methods=['POST'])
    def upvote(self, request, pk):
        """
        Upvote a post
        ---
        parameters_strategy:
            form: replace

        """
        post = self.get_object()
        post.downvotes.remove(request.user)
        post.upvotes.add(request.user)
        return Response(PostSerializer(post).data)

    @detail_route(methods=['POST'])
    def downvote(self, request, pk):
        """
        Downvote a post
        ---
        parameters_strategy:
            form: replace
        """
        post = self.get_object()
        post.upvotes.remove(request.user)
        post.downvotes.add(request.user)
        return Response(PostSerializer(post).data)
from rest_framework.viewsets import ModelViewSet
from .serializers import PostSerializer
from .models import Post, Reply, CONTENT_VISIBLE
from rest_framework.permissions import IsAuthenticated


class PostViewset(ModelViewSet):
    queryset = Post.objects.all().filter(visibility=CONTENT_VISIBLE)
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]



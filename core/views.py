from rest_framework import viewsets
from .models import Tag
from .serializers import TagSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import list_route
from rest_framework.response import Response


class TagViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]

    @list_route()
    def search(self, request):
        """
        Get list of tags by query
        ---
        serializer: core.serializers.TagSerializer
        parameters:
          - name: query
            type: string
            paramType: query

        """
        param = request.GET.get('query', '')
        tags = self.queryset.filter(tag__icontains=param)[:10]
        return Response(TagSerializer(tags, many=True).data)

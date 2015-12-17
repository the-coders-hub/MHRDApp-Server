from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import College
from .serializers import CollegeSerializer
from rest_framework.permissions import IsAuthenticated


class CollegeViewset(ReadOnlyModelViewSet):

    queryset = College.objects.all()
    serializer_class = CollegeSerializer
    permission_classes = [IsAuthenticated]


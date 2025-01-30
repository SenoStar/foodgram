from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from recipes.models import (
    Tag
)
from .serializers import (
    TagGetSerializer
)


class TagViewSet(viewsets.ModelViewSet):
    """Тег."""

    http_method_names = ['get']
    queryset = Tag.objects.all()
    serializer_class = TagGetSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated]
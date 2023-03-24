from django.shortcuts import render
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet

from recipes.models import Tag
from .serializers import TagSerializer


class TagsViewSet(ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer
    # pagination_class = None


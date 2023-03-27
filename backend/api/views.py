from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import Ingredient, Recipe, Tag
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import IngredientSerializer, TagSerializer


class TagsViewSet(ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientsViewSet(ReadOnlyModelViewSet):

    queryset = Ingredient.objects.all().order_by('id')
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = (r'^name',)

class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    # filter_backends = [DjangoFilterBackend]
    # filterset_class = RecipeFilter
    pagination_class = PageNumberPagination


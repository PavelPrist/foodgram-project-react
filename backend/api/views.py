from django.shortcuts import render, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import RecipeFilterSet
from .paginations import CustomPageNumberPagination
from recipes.models import Ingredient, Favorite, Recipe, ShoppingCart, Tag
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (
    IngredientSerializer,
    FavoriteSerializer,
    RecipeListGetSerializer,
    RecipePostSerializer,
    ShoppingCartSerializer,
    TagSerializer)



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
    queryset = Recipe.objects.all().order_by('name')
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilterSet
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListGetSerializer
        return RecipePostSerializer

    @staticmethod
    def post_actions(request, pk, serializers):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_actions(request, pk, model):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        object_ = model.objects.filter(user=user, recipe=recipe)
        if not object_.exists():
            return Response(
                "Объекта не существует",
                status=status.HTTP_400_BAD_REQUEST
            )
        object_.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.post_actions(
                request=request, pk=pk, serializers=FavoriteSerializer)
        if request.method == 'DELETE':
            return self.delete_actions(
                request=request, pk=pk, model=Favorite)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.post_actions(
                request=request, pk=pk, serializers=ShoppingCartSerializer)
        if request.method == 'DELETE':
            return self.delete_actions(
                request=request, pk=pk, model=ShoppingCart)



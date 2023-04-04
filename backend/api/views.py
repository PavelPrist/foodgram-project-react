from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (AmountOfIngredient, Favorite, Ingredient, Recipe,
                            ShoppingCart, Tag)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import RecipeFilterSet
from .paginations import CustomPageNumberPagination
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeListGetSerializer, RecipePostSerializer,
                          ShoppingCartSerializer, TagSerializer)


class TagsViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientsViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all().order_by('id')
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
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
        return None

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.post_actions(
                request=request, pk=pk, serializers=ShoppingCartSerializer)
        if request.method == 'DELETE':
            return self.delete_actions(
                request=request, pk=pk, model=ShoppingCart)
        return None

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopcart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        today = timezone.now()
        queryset = AmountOfIngredient.objects.select_related(
            'recipe', 'ingredient').filter(
            recipe__shopcart__user=request.user)

        ingredients_list = queryset.values_list(
            'ingredient__name', 'ingredient__measurement_unit',
            'recipe__name', 'amount')

        ingredients_sum_amount = queryset.values(
            'ingredient__name').annotate(sum_amount=Sum('amount'))

        ingredient_amount_dict = {}  # словарик:имя ингредиента и общ.колич.
        for item in ingredients_sum_amount:
            ingredient_amount_dict[
                item.get('ingredient__name')] = f'{item.get("sum_amount")}'

        pdfmetrics.registerFont(
            TTFont('FuturaOrto', 'data/FuturaOrto.ttf', 'UTF-8'))
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; '
            f'filename="{user.username}_shopping_list.pdf"'
        )
        page = canvas.Canvas(response)
        page.setFont('FuturaOrto', size=16)
        text = [
            'Спасибо, за покупки!',
            f'Пользователь: {user.get_full_name()}',
            f'Список покупок. '
            f'Дата: {today.day}, {today.month}, {today.year}'
        ]
        height = 800
        for text in text:
            page.drawString(
                150,
                height,
                text
            )
            height -= 30
        page.setFont('FuturaOrto', size=12)
        height = 700
        recipe_list = []
        name_ingredient_list = []
        for i, item in enumerate(ingredients_list):
            if item[0] not in name_ingredient_list:
                page.drawString(
                    75, height,
                    f'--{item[0]} - {ingredient_amount_dict[item[0]]} '
                    f'{item[1]}')
                height -= 20
                recipe_list = []
            if item[2] not in recipe_list:
                page.drawString(150, height, f'Рецепт-{item[2]}: ')
                height -= 30
                recipe_list.append(item[2])
            name_ingredient_list.append(item[0])
        page.showPage()
        page.save()
        return response

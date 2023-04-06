from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from users.models import User


class Tag(models.Model):
    color = models.CharField(
        'цветовой HEX-код тега',
        max_length=7,
        unique=True,
        help_text='Введите цвет тега',
    )
    name = models.CharField(
        'название',
        max_length=30,
        unique=True,
        help_text='Введите название тега',
    )
    slug = models.SlugField(
        'уникальный адрес',
        max_length=200,
        unique=True,
        help_text='Введите уникальный адрес',
    )

    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'тэги'
        ordering = ('name',)

    def __str__(self):
        return self.name[:15]


class Ingredient(models.Model):
    name = models.CharField(
        'название ингредиента',
        max_length=100,
    )
    measurement_unit = models.CharField(
        'единица измерения',
        max_length=50,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='unique_ingredient_and_unit')
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='автор',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField(
        'наименование рецепта',
        help_text='Наименование рецепта',
        max_length=200
    )
    image = models.ImageField(
        'изображение к рецепту',
        upload_to='recipes_img/%Y/%m/',
        help_text='Загрузите изображение рецепта'
    )
    text = models.TextField(
        'текст рецепта',
        help_text='Содержание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='AmountOfIngredient',
        related_name='recipes',
        verbose_name='ингредиенты для рецепта',
        help_text='Ингредиенты для рецепта',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='тэги рецепта',
        help_text='Тэги для рецепта',
    )
    cooking_time = models.PositiveIntegerField(
        'время приготовления блюда по рецепту',
        help_text='Время приготовления в минутах',
    )
    pub_date = models.DateTimeField(
        'дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'author'),
                name='recipe_name_unique')
        ]

    def __str__(self):
        return self.name

    @classmethod
    def get_shopping_cart(cls, user, request, response):
        today = timezone.now()
        queryset = AmountOfIngredient.get_queryset_recipe_users(
            request=request)
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


class RecipeBaseModel(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='рецепт',
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True


class UserBaseModel(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='пользователь',
    )

    class Meta:
        abstract = True


class AmountOfIngredient(RecipeBaseModel):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='название ингредиента',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField(
        verbose_name='количество ингредиента',
        validators=(
            MinValueValidator(
                1, message='Минимальное количество не меньше 1'),),
    )

    class Meta:
        default_related_name = 'amount'
        verbose_name = 'количество ингредиента в рецепте '
        ordering = ('ingredient',)

    def __str__(self):
        return self.ingredient.name

    @classmethod
    def get_queryset_recipe_users(cls, request):
        return cls.objects.select_related(
            'recipe', 'ingredient').filter(
            recipe__shopcart__user=request.user)


class Favorite(RecipeBaseModel, UserBaseModel):

    class Meta:
        default_related_name = 'favorite'
        verbose_name = 'избранное'
        verbose_name_plural = 'избранные'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique favorites')
        ]


class ShoppingCart(RecipeBaseModel, UserBaseModel):

    class Meta:
        default_related_name = 'shopcart'
        verbose_name = 'список покупок'
        verbose_name_plural = 'списки покупок'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique shopping_cart')
        ]

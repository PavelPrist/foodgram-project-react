from django.core.validators import MinValueValidator
from django.db import models

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
        upload_to='recipes_img/',
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
        help_text = 'Время приготовления в минутах',
    )
    pub_date = models.DateTimeField(
        'дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = "рецепт"
        verbose_name_plural = "рецепты"
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class AmountOfIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='название ингредиента',
        on_delete=models.CASCADE,
        related_name='amount',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='рецепт',
        on_delete=models.CASCADE,
        related_name='amount',
    )
    amount = models.PositiveIntegerField(
        verbose_name='количество ингредиента',
        validators=(
            MinValueValidator(
                1, message='Минимальное количество не меньше 1'),),
    )

    class Meta:
        verbose_name = "количество ингредиента в рецепте"
        ordering = ('ingredient',)
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'amount'],
                name='unique_amount_ingredient'
            )
        ]

    def __str__(self):
        return self.ingredient.name
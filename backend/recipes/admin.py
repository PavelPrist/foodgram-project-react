from django.contrib import admin

from .models import AmountOfIngredient, Ingredient, Recipe, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug'
    )
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit'
    )
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        'amount_favorites',
        'amount_tags',
        'amount_ingredients'
    )
    list_filter = (
        'author',
        'name',
        'tags'
    )
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(AmountOfIngredient)
class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'ingredient',
        'recipe',
        'amount'
    )
    empty_value_display = '-пусто-'

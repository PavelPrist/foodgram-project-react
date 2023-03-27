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

class RecipesIngredientsInline(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 3

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        Recipe.id.field.name,
        Recipe.name.field.name,
        Recipe.author.field.name,
        Recipe.text.field.name,
        Recipe.image.field.name,
        Recipe.cooking_time.field.name,
        Recipe.pub_date.field.name,
    )
    inlines = (RecipesIngredientsInline,)
    filter_horizontal = (Recipe.tags.field.name,)
    list_filter = (
        Recipe.author.field.name,
        Recipe.name.field.name,
        Recipe.tags.field.name
    )
    list_display_links = (Recipe.name.field.name, Recipe.id.field.name,)
    list_editable = (Recipe.text.field.name,)
    search_fields = (Recipe.name.field.name,)
    empty_value_display = '-пусто-'


@admin.register(AmountOfIngredient)
class AmountOfIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'ingredient',
        'recipe',
        'amount'
    )
    empty_value_display = '-пусто-'

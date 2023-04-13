from django.contrib import admin

from .models import (AmountOfIngredient, Favorite, Ingredient, Recipe,
                     ShoppingCart, Tag)


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
    model = AmountOfIngredient
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
        'amount_favorites'
    )
    fieldsets = (
        (None, {
            'fields': (('name', 'author'), 'text')
        }),
        ('Advanced options', {
            'classes': ('extrapretty',),
            'fields': ('tags',),
        }),
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
    readonly_fields = ('amount_favorites',)
    empty_value_display = '-пусто-'

    @staticmethod
    def get_end_letter(value):
        end_lib = {5: '', 2: 'а', 0: ''}
        for key in end_lib:
            if value % 10 >= key:
                return end_lib[key]
        return ''

    @admin.display(description='В избранном')
    def amount_favorites(self, obj):
        count_ = obj.favorite.count()
        end_letters = self.get_end_letter(obj.favorite.count())
        return (f'Рецепт добавлен в '
                f'избранное у авторов {count_} раз{end_letters}')


@admin.register(AmountOfIngredient)
class AmountOfIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'ingredient',
        'recipe',
        'amount'
    )
    empty_value_display = '-пусто-'


admin.site.register(Favorite)
admin.site.register(ShoppingCart)

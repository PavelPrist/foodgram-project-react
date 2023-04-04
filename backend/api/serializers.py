from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from recipes.models import (AmountOfIngredient, Favorite, Ingredient, Recipe,
                            ShoppingCart, Tag)
from users.serializers import CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = '__all__',


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = '__all__',


class RepresentationRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipe = data['recipe']
        if ShoppingCart.objects.filter(
                user=request.user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {'status': 'Рецепт уже есть в списке покупок'})
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RepresentationRecipeSerializer(
            instance.recipe, context=context).data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipe = data['recipe']
        if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {'status': 'Рецепт уже добавлен в избранное'})
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RepresentationRecipeSerializer(
            instance.recipe, context=context).data


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = AmountOfIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class AddIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = AmountOfIngredient
        fields = ('id', 'amount')


class RecipeListGetSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        ordering = ['name']
        read_only_fields = ('author',)

    def check_anonymous_help_func(self, obj, model):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return model.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_favorited(self, obj):
        return self.check_anonymous_help_func(obj=obj, model=Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.check_anonymous_help_func(obj=obj, model=ShoppingCart)

    def get_ingredients(self, obj):
        queryset = AmountOfIngredient.objects.filter(recipe=obj)
        return IngredientAmountSerializer(queryset, many=True).data


class RecipePostSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=100,
        validators=[UniqueValidator(
            queryset=Recipe.objects.all(),
            message='Рецепт с таким именем уже существует')],
    )
    ingredients = AddIngredientsSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'ingredients',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate(self, data):
        ingredients = data['ingredients']
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Добавьте хотя бы один ингредиент'
            })
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError({
                    'ingredients': 'Ингредиенты должны быть разными'
                })
            ingredients_list.append(ingredient_id)
            amount = ingredient['amount']
            if int(amount) <= 0:
                raise serializers.ValidationError({
                    'amount': 'Количество ингредиента должно быть больше нуля'
                })

        tags = data['tags']
        if not tags:
            raise serializers.ValidationError({
                'tags': 'Нужно выбрать хотя бы один тэг'
            })
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise serializers.ValidationError({
                    'tags': 'Тэги не должны повторяться'
                })
            tags_list.append(tag)

        cooking_time = data['cooking_time']
        if int(cooking_time) <= 0:
            raise serializers.ValidationError({
                'cooking_time': 'Время приготовления должно быть больше нуля'
            })
        return data

    @staticmethod
    def create_link_ingredients_recipe(ingredients_obj, recipe):
        for obj in ingredients_obj:
            AmountOfIngredient.objects.create(
                recipe=recipe,
                ingredient=obj['id'],
                amount=obj['amount']
            )

    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients_obj = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_link_ingredients_recipe(ingredients_obj, recipe)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients_obj = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.ingredients.clear()
        instance.tags.set(validated_data['tags'])
        self.create_link_ingredients_recipe(ingredients_obj, instance)
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeListGetSerializer(instance, context=context).data

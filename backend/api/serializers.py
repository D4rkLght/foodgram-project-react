from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Subscribe, Tag)

User = get_user_model()


class CreateUserSerializer(UserCreateSerializer):
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
        )],
        required=True,
    )

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        current_user = self.context.get('request').user
        if current_user.is_authenticated:
            return Subscribe.objects.filter(user=current_user,
                                            author=obj).exists()
        return False


class SubscribeSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscribe
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj.author)
        return recipes.values_list()

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def get_is_subscribed(self, obj):
        current_user = self.context.get('request').user
        if current_user.is_authenticated:
            return Subscribe.objects.filter(
                user=current_user,
                author=obj.author
            ).exists()
        return False

    def validate(self, data):
        if self.context.get('author') == self.context.get('request').user:
            raise ValidationError('Cant subscribe myself',
                                  HTTPStatus.BAD_REQUEST)
        return data


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('name', 'measurement_unit')


class IngredientAmountSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadOnlySerializer(serializers.ModelSerializer):
    author = UserSerializer()
    ingredients = IngredientAmountSerializer(
        many=True,
        source='recipe_amount',
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        current_user = self.context.get('request').user
        if current_user.is_authenticated:
            return Favorite.objects.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        current_user = self.context.get('request').user
        if current_user.is_authenticated:
            return ShoppingCart.objects.filter(recipe=obj).exists()
        return False


class AddAmountIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = AddAmountIngredientSerializer(
        many=True,
        write_only=True
    )
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('name', 'text', 'cooking_time', 'author',
                  'ingredients', 'tags', 'image',)

    def to_representation(self, instance):
        ingredients = super().to_representation(instance)
        ingredients['ingredients'] = IngredientAmountSerializer(
            instance.recipe_amount.all(), many=True).data
        return ingredients

    def add_ingredients(self, ingredients, model):
        recipe_ingredient = [IngredientAmount(
            ingredient=part['id'], recipe=model, amount=part['amount']
        ) for part in ingredients]
        IngredientAmount.objects.bulk_create(recipe_ingredient)

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance.ingredients.clear()
        self.add_ingredients(ingredients, instance)
        return super().update(instance, validated_data)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = super().create(validated_data)
        self.add_ingredients(ingredients, recipe)
        return recipe


class FavoriteSerializer(serializers.ModelSerializer):
    coocking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        read_only=True)
    id = serializers.PrimaryKeyRelatedField(
        source='recipe',
        read_only=True)
    name = serializers.ReadOnlyField(
        source='recipe.name',
        read_only=True)
    image = serializers.ImageField(
        source='recipe.image',
        read_only=True)

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'coocking_time')


class CartSerializer(serializers.ModelSerializer):
    coocking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        read_only=True)
    id = serializers.PrimaryKeyRelatedField(
        source='recipe',
        read_only=True)
    name = serializers.ReadOnlyField(
        source='recipe.name',
        read_only=True)
    image = serializers.ImageField(
        source='recipe.image',
        read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'coocking_time')

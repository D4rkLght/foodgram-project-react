from django.contrib.auth import get_user_model
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from rest_framework.validators import UniqueValidator
from recipes.models import Tag, Ingredient, Recipe, Favorite, Cart, Subscribe, IngredientAmount

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
        )],
        required=True,
    )
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 
                  'last_name', 'password', 'is_subscribed')
        model = User
        extra_kwargs = {'password': {'write_only': True}}
    
    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Subscribe.objects.filter(user=user, author=obj.author).exists()
        return False
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


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
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Subscribe.objects.filter(user=user, author=obj.author).exists()
        return False


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = '__all__',

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
        fields = '__all__'


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
        fields = '__all__'

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Favorite.objects.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Cart.objects.filter(recipe=obj).exists()
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
        fields = '__all__'
    
    def to_representation(self, instance):
        ingredients = super().to_representation(instance)
        ingredients['ingredients'] = IngredientAmountSerializer(
            instance.recipe_amount.all(), many=True).data
        return ingredients

    def add_ingredients(self, ingredients, model):
        for ingredient in ingredients:
            IngredientAmount.objects.update_or_create(
                recipe=model,
                ingredient=ingredient['id'],
                amount=ingredient['amount'])

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance.ingredients.clear()
        self.add_tingredients(ingredients, instance)
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
        model = Cart
        fields = ('id', 'name', 'image', 'coocking_time')

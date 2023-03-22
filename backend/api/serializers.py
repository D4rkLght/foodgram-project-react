from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Tag, Ingredient, Recipe

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    # author = serializers.SlugRelatedField(
    #     read_only=True,
    #     slug_field='username',
    # )
    image = Base64ImageField()
    class Meta:
        model = Recipe
        fields = '__all__'

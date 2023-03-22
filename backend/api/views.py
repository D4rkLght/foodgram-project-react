from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from recipes.models import Tag, Ingredient, Recipe

from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    # def perform_create(self, serializer):
    #     serializer.save(author=self.request.user)
from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag

User = get_user_model()


class IngredientFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        lookup_expr='in',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.NumberFilter(
        method='favorited_filter')
    is_in_shopping_cart = filters.NumberFilter(
        method='shopping_cart_filter')

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def favorited_filter(self, queryset, name, value):
        if value:
            return queryset.filter(in_favorites__user=self.request.user)
        return queryset.exclude(
            is_favorited=self.request.user
        )

    def shopping_cart_filter(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(
                in_cart__user=self.request.user
            )
        return Recipe.objects.all()

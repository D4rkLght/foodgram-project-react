from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .mixins import ListViewSet
from .paginations import Paginator
from .permissions import (IsAdminOrReadOnly, IsUserAdminOrReadOnly)
from .serializers import (CartSerializer, FavoriteSerializer,
                          IngredientSerializer, RecipeReadOnlySerializer,
                          RecipeWriteSerializer, SubscribeSerializer,
                          TagSerializer)
from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Subscribe, Tag)

User = get_user_model()


class UserUsualViewSet(UserViewSet):
    permission_classes = (IsUserAdminOrReadOnly,)
    pagination_class = Paginator

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscriptions(self, request):
        subscriptions = Subscribe.objects.filter(user=self.request.user)
        pages = self.paginate_queryset(subscriptions)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, *args, **kwargs):
        author = get_object_or_404(User, id=self.kwargs.get('id'))
        current_user = self.request.user
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                data=request.data,
                context={'request': request, 'author': author})
            serializer.is_valid(raise_exception=True)
            serializer.save(author=author, user=current_user)
            return Response(serializer.data, status=HTTPStatus.CREATED)
        elif request.method == 'DELETE':
            Subscribe.objects.get(author=author, user=current_user).delete()
            return Response(status=HTTPStatus.NO_CONTENT)
        return Response(status=HTTPStatus.NOT_FOUND)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = Paginator
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsUserAdminOrReadOnly)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return RecipeReadOnlySerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        current_user = self.request.user
        if request.method == 'POST':
            serializer = FavoriteSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=current_user, recipe=recipe)
            return Response(serializer.data, status=HTTPStatus.CREATED)
        elif request.method == 'DELETE':
            Favorite.objects.get(user=current_user, recipe=recipe).delete()
            return Response(status=HTTPStatus.NO_CONTENT)
        return Response(status=HTTPStatus.NOT_FOUND)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        filename = 'list_ingredients.txt'
        instance = request.user.cart.all()
        ingredients = IngredientAmount.objects.filter(
            recipe__in=instance.values('recipe')
        ).values('ingredient').annotate(amount=Sum('amount'))
        list_ingredients = []
        for ingredient in ingredients:
            amount = ingredient['amount']
            ingredient = Ingredient.objects.get(id=ingredient['ingredient'])
            measurement_unit = ingredient.measurement_unit
            list_ingredients.append(
                f'{ingredient} ({amount}) - {measurement_unit}'
            )
        response = Response(list_ingredients, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        current_user = self.request.user
        if request.method == 'POST':
            serializer = CartSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(author=current_user, recipe=recipe)
            return Response(serializer.data, status=HTTPStatus.CREATED)
        elif request.method == 'DELETE':
            ShoppingCart.objects.filter(author=current_user,
                                        recipe=recipe).delete()
            return Response(status=HTTPStatus.NO_CONTENT)
        return Response(status=HTTPStatus.NOT_FOUND)


class TagViewSet(ListViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class IngredientViewSet(ListViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)

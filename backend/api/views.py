import os

from http import HTTPStatus

from django.contrib.auth import get_user_model
from djoser.serializers import SetPasswordSerializer
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from recipes.models import Tag, Ingredient, Recipe, Favorite, Cart, Subscribe, IngredientAmount

from .serializers import TagSerializer, IngredientSerializer, RecipeReadOnlySerializer, RecipeWriteSerializer, FavoriteSerializer, CartSerializer, UserSerializer, SubscribeSerializer
from .paginations import Paginator
from .permissions import IsUserAdminOrReadOnly, IsOwnerAdminOrReadOnly

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = Paginator
    permission_classes = (IsUserAdminOrReadOnly,)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        user = self.request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def set_password(self, request, *args, **kwargs):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request})
        if serializer.is_valid(raise_exception=True):
            self.request.user.set_password(serializer.data.get("new_password"))
            self.request.user.save()
            return Response(status=HTTPStatus.NO_CONTENT)
        return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)
    
    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscriptions(self, request):
        subscriptions = Subscribe.objects.filter(user=self.request.user)
        serializer = SubscribeSerializer(
            subscriptions,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscribe(self, request, *args, **kwargs):
        author = get_object_or_404(User, id=self.kwargs.get('pk'))
        user = self.request.user
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                data=request.data,
                context={'request': request, 'author': author})
            if serializer.is_valid(raise_exception=True):
                serializer.save(author=author, user=user)
                return Response(serializer.data, status=HTTPStatus.CREATED)
            return Response(status=HTTPStatus.NOT_FOUND)
        if Subscribe.objects.filter(author=author, user=user).exists():
            Subscribe.objects.get(author=author).delete()
            return Response(status=HTTPStatus.NO_CONTENT)
        return Response(status=HTTPStatus.NOT_FOUND)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = Paginator
    permission_classes = (IsOwnerAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return RecipeReadOnlySerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        user = self.request.user
        if request.method == 'POST':
            serializer = FavoriteSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(user=user, recipe=recipe)
                return Response(serializer.data, status=HTTPStatus.CREATED)
            return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            Favorite.objects.get(user=user).delete()
            return Response(status=HTTPStatus.NO_CONTENT)
        return Response(status=HTTPStatus.NOT_FOUND)
    
    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        
        return ...

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        user = self.request.user
        if request.method == 'POST':
            serializer = CartSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(user=user, recipe=recipe)
                return Response(serializer.data, status=HTTPStatus.CREATED)
            return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)
        if Cart.objects.filter(user=user, recipe=recipe).exists():
            Cart.objects.get(user=user).delete()
            return Response(status=HTTPStatus.NO_CONTENT)
        return Response(status=HTTPStatus.NOT_FOUND)


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
from django.db.models import Sum
from http import HTTPStatus

from django.contrib.auth import get_user_model
from djoser.serializers import SetPasswordSerializer
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from recipes.models import Tag, Ingredient, Recipe, Favorite, Cart, Subscribe, IngredientAmount

from .filters import RecipeFilter
from .mixins import ListViewSet
from .serializers import TagSerializer, IngredientSerializer, RecipeReadOnlySerializer, RecipeWriteSerializer, FavoriteSerializer, CartSerializer, UserSerializer, SubscribeSerializer
from .paginations import Paginator
from .permissions import IsUserAdminOrReadOnly, IsOwnerAdminOrReadOnly, IsAdminOrReadOnly

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


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = Paginator
    permission_classes = (IsOwnerAdminOrReadOnly,)
    filterset_class = RecipeFilter

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
        filename = 'list_ingredients.pdf'
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
                f'{ingredient} ({amount}) — {measurement_unit}'
            )
        response = Response(list_ingredients, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

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
                serializer.save(author=user, recipe=recipe)
                return Response(serializer.data, status=HTTPStatus.CREATED)
            return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)
        if Cart.objects.filter(author=user, recipe=recipe).exists():
            Cart.objects.get(author=user).delete()
            return Response(status=HTTPStatus.NO_CONTENT)
        return Response(status=HTTPStatus.NOT_FOUND)


class TagViewSet(ListViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(ListViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)

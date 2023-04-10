from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Name',
        max_length=50,
        unique=True
    )
    color = models.CharField(
        verbose_name='Color',
        unique=True,
        max_length=7
    )
    slug = models.SlugField(
        verbose_name='Slug',
        max_length=50,
        unique=True,
    )

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Ingredient',
        unique=True,
    )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name='Unit',
    )

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
        ordering = ('name', )

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Ingredients',
        through='IngredientAmount',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Tags'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Author',
    )
    image = models.ImageField(
        upload_to='images/',
        verbose_name='Image',
    )
    name = models.CharField(
        max_length=50,
        verbose_name='Recipe name',
    )
    text = models.TextField(verbose_name='Description')
    cooking_time = models.IntegerField(
        validators=[
            MinValueValidator(1, 'Minimal cooking time')
        ],
        verbose_name='Cooking time'
    )
    pub_date = models.DateTimeField(
        verbose_name='Publication date',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        ordering = ('-pub_date', )
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='unique_recipe')
        ]

    def __str__(self) -> str:
        return self.name


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ingredient',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_amount',
        verbose_name='Recipe',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, 'Minimal amount')
        ],
        verbose_name='Amount',
    )

    class Meta:
        verbose_name = 'Ingredients recipe'
        verbose_name_plural = 'Ingredients recipes'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredients')]

    def __str__(self):
        return f'{self.ingredient} ({self.amount})'


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='in_favorites',
        on_delete=models.CASCADE,
        verbose_name='Recipe',
    )
    user = models.ForeignKey(
        User,
        related_name='favorites',
        on_delete=models.CASCADE,
        verbose_name='Author',
    )
    pub_date = models.DateTimeField(
        verbose_name='Publication date',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Favorite recipe'
        verbose_name_plural = 'Favorite recipes'

    def __str__(self):
        return self.recipe


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='in_cart',
        on_delete=models.CASCADE,
        verbose_name='Recipe',
    )
    author = models.ForeignKey(
        User,
        related_name='cart',
        on_delete=models.CASCADE,
        verbose_name='User',
    )
    pub_date = models.DateTimeField(
        verbose_name='Publication date',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Shopping cart'
        verbose_name_plural = 'Shopping carts'

    def __str__(self):
        return self.recipe


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='User',
        related_name='in_subscribe',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Subscription',
        related_name='subscribe',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Subscribe'
        verbose_name_plural = 'Subscribes'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'),
        ]

    def __str__(self):
        return f'User {self.user} subccribed to {self.author}'

from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True
    )
    color = models.CharField(max_length=7)
    slug = models.SlugField(unique=True,)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ('name',)
    
    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='Ingredient',
        db_index=True,
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
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')
    name = models.CharField(max_length=50,)
    text = models.TextField()
    cooking_time = models.IntegerField()
    pub_date = models.DateTimeField(
        verbose_name='Publication date',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        ordering = ('-pub_date', )

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
 

class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='in_favorites',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        related_name='favorites',
        on_delete=models.CASCADE,
    )
    pub_date = models.DateTimeField(
        verbose_name='Publication date',
        auto_now_add=True,
    )
    class Meta:
        verbose_name = 'Favorite recipe'
        verbose_name_plural = 'Favorite recipes'


class Cart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='in_cart',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='cart',
        on_delete=models.CASCADE,
    )
    pub_date = models.DateTimeField(
        verbose_name='Publication date',
        auto_now_add=True,
    )
    class Meta:
        verbose_name = 'Shopping cart'
        verbose_name_plural = 'Shopping carts'


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

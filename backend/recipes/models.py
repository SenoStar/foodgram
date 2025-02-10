from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models

from .constants import (
    LEN_32,
    LEN_64,
    LEN_128,
    LEN_150,
    LEN_254,
    LEN_256
)
from .validators import user_username_validator


class User(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=LEN_254,
        unique=True
    )
    username = models.CharField(
        verbose_name='Уникальный юзернейм',
        max_length=LEN_150,
        unique=True,
        validators=[user_username_validator]
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=LEN_150
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=LEN_150
    )
    avatar = models.ImageField(
        upload_to='users/',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']


class Subscription(models.Model):
    """Подписки пользователей."""

    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='following'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='follower'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['author']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='user_author'
            ),
        ]

    def __str__(self):
        return self.author.username


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        verbose_name='Название',
        max_length=LEN_32,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Slug',
        max_length=LEN_32,
        unique=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""

    ingredients = models.ManyToManyField(
        'Ingredient',
        verbose_name='Список ингредиентов',
        related_name='recipes',
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Список id тегов',
        related_name='recipes'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        null=False
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=LEN_256,
        unique=True,
        null=False
    )
    text = models.TextField(
        verbose_name='Описание',
        null=False
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        null=False,
        validators=[MinValueValidator(1)]
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='authored_recipes'
    )
    published_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        null=False
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-published_date']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(
        verbose_name='Название',
        max_length=LEN_128,
        db_index=True,
        unique=True
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=LEN_64,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Связующая модель рецепт-ингредиент."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        db_table = 'recipes_recipe_ingredient'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.ingredient.name} {self.recipe.name}'


class Favorite(models.Model):
    """Модель избранного."""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='favorites',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ['recipe__name']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='user_favorite'
            )
        ]

    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}'


class ShoppingCart(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.recipe} в списке покупок у {self.user}'

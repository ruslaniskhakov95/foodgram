from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

from api.constants import MAX_NAME_LENGTH, MAX_SLUG_LENGTH, LIMIT_TEXT


User = get_user_model()


# Decide whether purchase unique together constraint is necessary


class BaseModel(models.Model):
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        unique=True,
        verbose_name='Название'
    )

    class Meta:
        abstract = True
        verbose_name = 'Базовая модель'


class Ingredient(BaseModel):
    measurement_unit = models.CharField(
        max_length=MAX_SLUG_LENGTH,
        verbose_name='Единицы измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name[:LIMIT_TEXT]


class Tag(BaseModel):
    slug = models.SlugField(
        max_length=MAX_SLUG_LENGTH,
        unique=True,
        verbose_name='Slug'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('slug',)

    def __str__(self):
        return self.slug[:LIMIT_TEXT]


class Recipe(BaseModel):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    image = models.ImageField(
        upload_to='users/images/',
        verbose_name='Картинка'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиент'
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        verbose_name='Тэг рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[MinValueValidator(1), MaxValueValidator(1440)]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name',)

    def __str__(self):
        return self.name[:LIMIT_TEXT]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Название рецепта',
        related_name='recipe_for_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='ingredients_for_recipe'
    )
    amount = models.IntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Рецепт - ингредиент'
        verbose_name_plural = 'Рецепт - ингредиент'
        ordering = ['recipe__name']

    def __str__(self):
        return (f'Рецепт {self.recipe__name} - '
                f'Ингредиент {self.ingredient__name}')


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Название рецепта',
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег'
    )

    class Meta:
        verbose_name = 'Рецепт - Тег'
        verbose_name_plural = 'Рецепт - Тег'
        ordering = ['recipe__name']

    def __str__(self):
        return (f'Рецепт {self.recipe__name} - '
                f'Тег {self.tag__name}')


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='liker',
        verbose_name='Пользователь'
    )
    favorite = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorite',
        verbose_name='Избранный рецепт'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'favorite'), name='unique_user_favorite'
            )
        ]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='buyer',
    )
    purchase = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='purchase',
        verbose_name='Покупка'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'purchase'), name='unique_user_purchase'
            )
        ]
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'

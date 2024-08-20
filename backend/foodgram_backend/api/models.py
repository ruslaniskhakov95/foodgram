from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api.constants import LIMIT_TEXT, MAX_NAME_LENGTH, MAX_SLUG_LENGTH

User = get_user_model()


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
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

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
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'), name='recipe_ingr_unique'
            )
        ]

    def __str__(self):
        return (f'Рецепт "{self.recipe.name}" - '
                f'Ингредиент "{self.ingredient.name}"')


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Название рецепта',
        related_name='recipe_tag'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег',
        related_name='tag_for_recipe'
    )

    class Meta:
        verbose_name = 'Рецепт - Тег'
        verbose_name_plural = 'Рецепт - Тег'
        ordering = ['recipe__name']
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'tag'), name='recipe_tag_unique'
            )
        ]

    def __str__(self):
        return (f'Рецепт "{self.recipe.name}" - '
                f'Тег "{self.tag.name}"')


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
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return (f'Пользователь {self.user.username} - '
                f'Избранный рецепт "{self.favorite.name}"')


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='buyer',
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe',
        verbose_name='Рецепт в списке покупок'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'), name='unique_user_purchase'
            )
        ]
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'

    def __str__(self):
        return (f'Пользователь {self.user.username} - '
                f'Рецепт в корзине "{self.recipe.name}"')

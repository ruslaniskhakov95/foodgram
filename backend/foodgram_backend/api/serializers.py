from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from rest_framework import serializers, validators
from users.serializers import Base64ImageField, CustomUserSerializer

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient, RecipeTag,
                     ShoppingCart, Tag)

User = get_user_model()


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=False)
    name = serializers.CharField(required=False)
    measurement_unit = serializers.CharField(required=False)
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_amount(self, obj):
        request = self.context['request']
        if request.method == 'GET':
            recipe = Recipe.objects.get(id=self.context.get('recipe_id'))
        else:
            recipe = Recipe.objects.get(
                name=self.context['request'].data.get('name')
            )
        amount = RecipeIngredient.objects.get(
            recipe=recipe, ingredient=obj
        ).amount
        if amount < 1:
            raise serializers.ValidationError('Amount should be >= 1!')
        return amount


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField(required=False)
    slug = serializers.SlugField(
        validators=[validators.UniqueValidator(queryset=Tag.objects.all())],
        required=False
    )

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class RecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, read_only=True)
    ingredients = IngredientAmountSerializer(many=True)
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(default=serializers.CurrentUserDefault())
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(allow_null=True, required=False)
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = (
            'id', 'ingredients', 'tags', 'author', 'is_favorited',
            'is_in_shopping_cart', 'image', 'name', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user, favorite=obj
            ).exists()
        else:
            return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        else:
            return False

    def to_internal_value(self, data):
        data['tags'] = [{'id': tag} for tag in data['tags']]
        return super().to_internal_value(data)

    def to_representation(self, instance):
        self.context['recipe_id'] = instance.id
        return super().to_representation(instance)

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        for ingredient in ingredients:
            if int(ingredient['amount']) < 1:
                raise serializers.ValidationError(
                    'Cannot use ingr with amount < 1!'
                )
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Recipe MUST contain at least one ingredient!'
            )
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            try:
                current_ingredient = Ingredient.objects.get(
                    id=ingredient.get('id')
                )
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    'There is no such ingredient!'
                )
            try:
                RecipeIngredient.objects.create(
                    recipe_id=recipe.id, ingredient_id=current_ingredient.id,
                    amount=ingredient.get('amount')
                )
            except IntegrityError:
                raise serializers.ValidationError(
                    'You cannot use one ingredient twice!'
                )
        for tag in tags:
            try:
                current_tag = Tag.objects.get(id=tag.get('id'))
            except Tag.DoesNotExist:
                raise serializers.ValidationError('Tag does not exist')
            try:
                RecipeTag.objects.create(
                    recipe=recipe, tag_id=current_tag.id
                )
            except IntegrityError:
                raise serializers.ValidationError(
                    'You cannot use this tag twice!'
                )
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.save()
        to_del = RecipeIngredient.objects.filter(recipe=instance.id)
        to_del.delete()
        to_del = RecipeTag.objects.filter(recipe=instance.id)
        to_del.delete()
        ingredients = self.initial_data.get('ingredients')
        for ingredient in ingredients:
            try:
                current_ingredient = Ingredient.objects.get(
                    id=ingredient.get('id')
                )
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError('No such ingredient')
            try:
                RecipeIngredient.objects.create(
                    recipe_id=instance.id,
                    ingredient_id=current_ingredient.id,
                    amount=ingredient.get('amount')
                )
            except IntegrityError:
                raise serializers.ValidationError(
                    'You cannot use one ingredient twice!'
                )
        for tag in tags:
            try:
                current_tag = Tag.objects.get(id=tag['id'])
            except Tag.DoesNotExist:
                raise serializers.ValidationError('No such Tag!')
            try:
                RecipeTag.objects.create(
                    recipe=instance, tag_id=current_tag.id
                )
            except IntegrityError:
                raise serializers.ValidationError(
                    'You cannot use this tag twice!'
                )
        return instance


class RecipeIsFavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('user', 'favorite')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'favorite')
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe')
            )
        ]

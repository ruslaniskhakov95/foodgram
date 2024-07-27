from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers, validators

from .models import (
    Tag, Ingredient, Recipe, RecipeIngredient, RecipeTag, Favorite,
    ShoppingCart
)
from users.serializers import Base64ImageField, CustomUserSerializer


User = get_user_model()

# Look whether CHOICES for measurement_units for Ingredient model are necessary


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
        return RecipeIngredient.objects.get(
            recipe=recipe, ingredient=obj
        ).amount


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
    author = CustomUserSerializer(default=serializers.CurrentUserDefault())
    image = Base64ImageField()
    ingredients = IngredientAmountSerializer(many=True)
    tags = TagSerializer(many=True)
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = (
            'id', 'ingredients', 'tags', 'image', 'name',
            'text', 'cooking_time', 'author'
        )

    def to_internal_value(self, data):
        data['tags'] = [{'id': tag} for tag in data['tags']]
        return super().to_internal_value(data)

    def to_representation(self, instance):
        self.context['recipe_id'] = instance.id
        return super().to_representation(instance)

    def create(self, validated_data):
        if 'ingredients' not in self.initial_data:
            raise serializers.ValidationError('No ingredients in recipe!')
        if 'tags' not in self.initial_data:
            raise serializers.ValidationError('No tags assigned!')
        ingredients = validated_data.pop('ingredients')
        ingredients = self.initial_data.get('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            current_ingredient = get_object_or_404(
                Ingredient, id=ingredient.get('id')
            )
            RecipeIngredient.objects.create(
                recipe_id=recipe.id, ingredient_id=current_ingredient.id,
                amount=ingredient.get('amount')
            )
        for tag in tags:
            current_tag = get_object_or_404(
                Tag, id=tag['id']
            )
            RecipeTag.objects.create(
                recipe=recipe, tag_id=current_tag.id
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
            current_ingredient = get_object_or_404(
                Ingredient, id=ingredient.get('id')
            )
            RecipeIngredient.objects.create(
                recipe_id=instance.id, ingredient_id=current_ingredient.id,
                amount=ingredient.get('amount')
            )
        for tag in tags:
            current_tag = get_object_or_404(
                Tag, id=tag['id']
            )
            RecipeTag.objects.create(
                recipe=instance, tag_id=current_tag.id
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

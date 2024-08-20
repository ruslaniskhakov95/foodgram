from django_filters import filters, filterset
from rest_framework import mixins, viewsets

from .models import Ingredient, Recipe, Tag


class CreateDestroyViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    pass


class RecipeFilter(filterset.FilterSet):
    author = filters.CharFilter(
        field_name='author__id', lookup_expr='exact'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags']


class IngredientFilter(filterset.FilterSet):
    name = filters.CharFilter(
        field_name='name', lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ['name']

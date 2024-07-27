from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.urls import reverse
from shortener.models import UrlMap
from shortener import shortener
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Tag, Ingredient, Recipe
from .serializers import (
    TagSerializer, IngredientSerializer, RecipeSerializer
)


User = get_user_model()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)

    @action(
        methods=['get'], detail=True, url_path='get-link'
    )
    def get_short_link(self, request, pk):
        """Получение короткой ссылки на рецепт"""

        recipe = get_object_or_404(Recipe, pk=pk)
        if not recipe:
            raise ValueError('No recipe to process')
        protocol_host = request.scheme + '://' + request.META.get(
            'HTTP_HOST'
        )
        origin_path = reverse('recipes-detail', args=(pk,))
        origin_url = f'{protocol_host}{origin_path}'
        if UrlMap.objects.filter(full_url=origin_url).exists():
            existing_link = UrlMap.objects.get(full_url=origin_url)
            short_link = f'{protocol_host}/s/{existing_link.short_url}'
            return Response(
                {'short-link': short_link}, status=status.HTTP_200_OK
            )
        if request.user.is_authenticated:
            link = shortener.create(user=request.user, link=origin_url)
        else:
            admin = User.objects.filter(is_staff=True).first()
            link = shortener.create(user=admin, link=origin_url)
        short_link = f'{protocol_host}/s/{link}'
        return Response(
            {'short-link': short_link}, status=status.HTTP_200_OK
        )

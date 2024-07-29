from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from shortener.models import UrlMap
from shortener import shortener
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    Tag, Ingredient, Recipe, Favorite, ShoppingCart, RecipeIngredient
)
from .serializers import (
    TagSerializer, IngredientSerializer, RecipeSerializer, FavoriteSerializer,
    RecipeIsFavoriteSerializer, ShoppingCartSerializer
)
from .utils import CreateDestroyViewSet


User = get_user_model()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['get']


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['get']


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter
    ]
    filterset_fields = (
        'author', 'tags'
    )
    search_fields = ('name',)
    ordering_fields = ('-pub_date',)

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)

    @action(
        methods=['get'], detail=True, url_path='get-link',
        permission_classes=[permissions.AllowAny]
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

    @action(
        methods=['get'], detail=False,
        url_path='download_shopping_cart'
    )
    def get_shopping_cart(self, request):
        user = request.user
        queryset = ShoppingCart.objects.filter(user=user).prefetch_related(
            Prefetch('recipe', to_attr='recipe_to_cart')
        )
        recipes_to_cart = [obj.recipe_to_cart for obj in queryset]
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=shopcart.txt'
        temp = []
        for recipe in recipes_to_cart:
            ingredient_set = RecipeIngredient.objects.filter(recipe=recipe)
            for recipe_ingredient in ingredient_set:
                flag = False
                for c in temp:
                    if c[0] == recipe_ingredient.ingredient.name:
                        c[1] += recipe_ingredient.amount
                        flag = True
                if not flag:
                    current_ingr = [
                        recipe_ingredient.ingredient.name,
                        recipe_ingredient.amount,
                        recipe_ingredient.ingredient.measurement_unit
                    ]
                    temp.append(current_ingr)
        lines = []
        for t in temp:
            lines.append(f'{t[0]} - {t[1]} {t[2]}.\n')
        response.writelines(lines)
        return response


class FavoriteViewSet(CreateDestroyViewSet):

    def create(self, request, *args, **kwargs):
        favorite_id = kwargs.get('pk', None)
        recipe = get_object_or_404(Recipe, id=favorite_id)
        if favorite_id:
            data = {
                'user': request.user.id,
                'favorite': favorite_id
            }
            serializer = FavoriteSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            recipe_serializer = RecipeIsFavoriteSerializer(recipe)
            return Response(
                recipe_serializer.data, status=status.HTTP_201_CREATED
            )
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        favorite_id = kwargs.get('pk', None)
        recipe = get_object_or_404(Recipe, id=favorite_id)
        if favorite_id:
            favorite = get_object_or_404(
                Favorite, user=request.user, favorite=recipe
            )
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ShoppingCartViewSet(CreateDestroyViewSet):

    def create(self, request, *args, **kwargs):
        recipe_to_buy_id = kwargs.get('pk', None)
        recipe = get_object_or_404(Recipe, id=recipe_to_buy_id)
        if recipe_to_buy_id:
            data = {
                'user': request.user.id,
                'recipe': recipe_to_buy_id
            }
            serializer = ShoppingCartSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            recipe_serializer = RecipeIsFavoriteSerializer(recipe)
            return Response(
                recipe_serializer.data, status=status.HTTP_201_CREATED
            )
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        recipe_to_buy_id = kwargs.get('pk', None)
        recipe = get_object_or_404(Recipe, id=recipe_to_buy_id)
        if recipe_to_buy_id:
            recipe_to_buy = get_object_or_404(
                ShoppingCart, user=request.user, recipe=recipe
            )
            recipe_to_buy.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

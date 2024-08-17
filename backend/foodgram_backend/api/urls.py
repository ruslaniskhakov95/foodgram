from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (FavoriteViewSet, IngredientViewSet, RecipeViewSet,
                    ShoppingCartViewSet, TagViewSet)

api_router_v1 = DefaultRouter()
api_router_v1.register('tags', TagViewSet, basename='tags')
api_router_v1.register(
    'ingredients', IngredientViewSet, basename='ingredients'
)
api_router_v1.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('', include(api_router_v1.urls)),
    path(
        'recipes/<int:pk>/favorite/', FavoriteViewSet.as_view(
            {
                'post': 'create',
                'delete': 'destroy'
            }
        )
    ),
    path(
        'recipes/<int:pk>/shopping_cart/', ShoppingCartViewSet.as_view(
            {
                'post': 'create',
                'delete': 'destroy'
            }
        )
    )
]

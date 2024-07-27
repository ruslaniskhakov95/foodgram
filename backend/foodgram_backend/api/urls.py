from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TagViewSet, IngredientViewSet, RecipeViewSet

api_router_v1 = DefaultRouter()
api_router_v1.register('tags', TagViewSet, basename='tags')
api_router_v1.register(
    'ingredients', IngredientViewSet, basename='ingredients'
)
api_router_v1.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('', include(api_router_v1.urls))
]
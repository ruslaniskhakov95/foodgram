from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet, SubscribeViewSet

app_name = 'users'

router_api_users = DefaultRouter()
# router_api_users.register(
#    r'users/(?P<subscribing_id>\d+)/subscribe', SubscribeViewSet,
#    basename='subscribe'
# )
router_api_users.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router_api_users.urls)),
    path(
        'users/<int:pk>/subscribe/', SubscribeViewSet.as_view({
            'post': 'create',
            'delete': 'destroy'
        }), name='subscribe'
    )
]

from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from api.utils import CreateDestroyViewSet
from .models import User, Subscribe
from .serializers import (
    CustomUserSerializer, SubscribeSerializer, EnlargedSubscribeUser
)

# insert permissions, pagination, search and filter classes


class SubscribeViewSet(CreateDestroyViewSet):

    def create(self, request, *args, **kwargs):
        subscribe_to_id = kwargs.get('pk', None)
        if subscribe_to_id:
            data = {
                'user': request.user,
                'subscribing': subscribe_to_id
            }
            serializer = SubscribeSerializer(
                data=data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            subscribe_to_user = get_object_or_404(User, id=subscribe_to_id)
            response_serializer = CustomUserSerializer(
                subscribe_to_user, context={'request': request}
            )
            return Response(
                response_serializer.data, status=status.HTTP_201_CREATED
            )
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request,  *args, **kwargs):
        subscribing_id = kwargs.get('pk', None)
        if subscribing_id:
            subscribe = get_object_or_404(
                Subscribe, user=request.user, subscribing=subscribing_id
            )
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]

    @action(
        methods=['get'], detail=False, url_path='me',
        permission_classes=[permissions.IsAuthenticated]
    )
    def user_info(self, request):
        user = request.user
        serializer = CustomUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['put', 'delete'], detail=False, url_path='me/avatar',
        permission_classes=[permissions.IsAuthenticated]
    )
    def avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            data = request.data
            status_code = status.HTTP_200_OK
        if request.method == 'DELETE':
            data = {'avatar': None}
            status_code = status.HTTP_204_NO_CONTENT

        serializer = CustomUserSerializer(
            user, data=data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status_code)

    @action(
        methods=['post',], detail=False, url_path='set_password',
        permission_classes=[permissions.IsAuthenticated]
    )
    def set_password(self, request):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        if new_password:
            serializer = CustomUserSerializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            if user.check_password(current_password):
                user.set_password(new_password)
                user.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    'Неверный пароль', status=status.HTTP_401_UNAUTHORIZED
                )
        else:
            raise ValueError('Пароль не может содержать пустую строку!')

    @action(
        detail=False, url_path='subscriptions',
        permission_classes=[permissions.IsAuthenticated]
    )
    def get_subscriptions_list(self, request):
        user = request.user
        queryset = Subscribe.objects.filter(user=user).prefetch_related(
            Prefetch('subscribing', to_attr='subscribed_to_user')
        )
        subscribed_to_users = [obj.subscribed_to_user for obj in queryset]
        if queryset:
            serializer = EnlargedSubscribeUser(
                subscribed_to_users, many=True, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise ValueError('Текущий пользователь ни на кого не подписан!')

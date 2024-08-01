from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from api.utils import CreateDestroyViewSet
from .models import User, Subscribe
from .serializers import (
    CustomUserSerializer, CreateUserSerializer,
    SubscribeSerializer, EnlargedSubscribeUser
)


class SubscribeViewSet(CreateDestroyViewSet):

    def create(self, request, *args, **kwargs):
        subscribe_to_id = kwargs.get('pk', None)
        subscribing = get_object_or_404(User, id=subscribe_to_id)
        data = {
            'user': request.user,
            'subscribing': subscribing.id
        }
        serializer = SubscribeSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_serializer = EnlargedSubscribeUser(
            subscribing, context={'request': request}
        )
        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED
        )

    def destroy(self, request,  *args, **kwargs):
        subscribing_id = kwargs.get('pk', None)
        subscribing = get_object_or_404(User, id=subscribing_id)
        try:
            subscribe = Subscribe.objects.get(
                user=request.user, subscribing=subscribing.id
            )
        except Subscribe.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserSerializer
        return CustomUserSerializer

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
            if request.data.get('avatar'):
                serializer = CustomUserSerializer(
                    user, data=data, partial=True
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(
                    {'avatar': serializer.data.get('avatar')},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            data = {'avatar': None}
            serializer = CustomUserSerializer(
                user, data=data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return None

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
                    'Неверный пароль', status=status.HTTP_400_BAD_REQUEST
                )
        else:
            raise ValueError('Пароль не может содержать пустую строку!')

    @action(
        detail=False, url_path='subscriptions',
        permission_classes=[permissions.IsAuthenticated],
        pagination_class=LimitOffsetPagination
    )
    def get_subscriptions_list(self, request):
        user = request.user
        queryset = Subscribe.objects.filter(user=user).prefetch_related(
            Prefetch('subscribing', to_attr='subscribed_to_user')
        )
        subscribed_to_users = [obj.subscribed_to_user for obj in queryset]
        page = self.paginate_queryset(subscribed_to_users)
        if page is not None:
            serializer = EnlargedSubscribeUser(
                subscribed_to_users, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        if queryset:
            serializer = EnlargedSubscribeUser(
                subscribed_to_users, many=True, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise ValueError('Текущий пользователь ни на кого не подписан!')

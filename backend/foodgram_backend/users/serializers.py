import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers, validators

from .models import User, Subscribe


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class CustomUserSerializer(UserSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True
    )
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar', 'password'
        )

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data.get('password'))
        user.save()
        return user

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        subscribing = User.objects.get(username=obj.username)
        if request and request.user.is_authenticated:
            return Subscribe.objects.filter(
                user=request.user.id, subscribing=subscribing
            ).exists()
        else:
            return False


class SubscribeSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    subscribing = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = Subscribe
        fields = (
            'user', 'subscribing'
        )
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'subscribing')
            )
        ]

    def validate(self, data):
        if self.context['request'].user == data.get('subscribing'):
            raise serializers.ValidationError('Подписываться на себя нельзя!')
        return data

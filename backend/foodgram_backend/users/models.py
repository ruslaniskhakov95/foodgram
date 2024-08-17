from api.constants import MAX_EMAIL_LENGTH, MAX_NAME_LENGTH
from api.validators import username_validator
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    '''Модель пользователя'''

    username = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Имя пользователя',
        unique=True,
        validators=[username_validator],
        error_messages={
            'unique': 'Пользователь с таким именем уже существует'
        }
    )
    first_name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Фамилия'
    )
    email = models.EmailField(
        unique=True,
        max_length=MAX_EMAIL_LENGTH,
        verbose_name='Адрес электронной почты'
    )
    avatar = models.ImageField(
        upload_to='users/images/',
        blank=True,
        default=None,
        verbose_name='Аватар'
    )
    password = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Пароль'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    '''Модель подписки'''

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='Subscriber',
        verbose_name='Пользователь'
    )
    subscribing = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='Subscribing',
        verbose_name='Подписка'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'subscribing'), name='unique_user_subscribing'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return self.subscribing

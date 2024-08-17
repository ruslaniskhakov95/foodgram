import re

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator

validate_min_time = [MinValueValidator(1)]
validate_max_time = [MaxValueValidator(1440)]


def username_validator(value):
    if value == 'me':
        raise ValidationError('Имя "me" недопустимо для использования.')
    if not re.fullmatch(r'^[\w.@+-]+$', value):
        raise ValidationError('Имя пользователя не соответствует шаблону.')
    return value

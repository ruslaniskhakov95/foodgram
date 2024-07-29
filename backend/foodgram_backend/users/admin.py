from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class FoodgramAdmin(UserAdmin):
    search_fields = ('username', 'email')


FoodgramAdmin.fieldsets += (
    ('Extra Fields', {'fields': ('avatar',)}),
)

admin.site.register(User, FoodgramAdmin)

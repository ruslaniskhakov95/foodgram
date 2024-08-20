from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscribe, User


class FoodgramAdmin(UserAdmin):
    search_fields = ('username', 'email')


FoodgramAdmin.fieldsets += (
    ('Extra Fields', {'fields': ('avatar',)}),
)

admin.site.register(User, FoodgramAdmin)
admin.site.register(Subscribe)

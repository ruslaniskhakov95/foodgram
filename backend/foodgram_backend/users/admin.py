from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin

from .models import Subscribe, User


class FoodgramAdmin(UserAdmin):
    search_fields = ('username', 'email')


class SubscribeAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        if obj.user == obj.subscribing:
            messages.set_level(request, messages.ERROR)
            message = 'User cannot subscribe on himself!!'
            self.message_user(request, message, level=messages.ERROR)
        else:
            obj.save()


FoodgramAdmin.fieldsets += (
    ('Extra Fields', {'fields': ('avatar',)}),
)

admin.site.register(User, FoodgramAdmin)
admin.site.register(Subscribe, SubscribeAdmin)

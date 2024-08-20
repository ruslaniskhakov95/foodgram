from django.contrib import admin, messages

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient, RecipeTag,
                     ShoppingCart, Tag)


class IngredientInLine(admin.StackedInline):
    model = RecipeIngredient
    min_num = 1
    extra = 1
    can_delete = False


class TaginLine(admin.StackedInline):
    model = RecipeTag
    min_num = 1
    extra = 1
    can_delete = False


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    search_fields = ('name', 'author')
    list_filter = ('tags',)
    inlines = (IngredientInLine, TaginLine)
    filter_horizontal = ('tags', 'ingredients')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class RecipeIngredientAdmin(admin.ModelAdmin):

    def delete_model(self, request, obj):
        queryset = RecipeIngredient.objects.filter(recipe=obj.recipe)
        if queryset.count() == 1:
            messages.set_level(request, messages.ERROR)
            message = 'You cannot delete the only one ingredient!'
            self.message_user(request, message, level=messages.ERROR)
        else:
            obj.delete()


class RecipeTagAdmin(admin.ModelAdmin):

    def delete_model(self, request, obj):
        queryset = RecipeTag.objects.filter(recipe=obj.recipe)
        if queryset.count() == 1:
            messages.set_level(request, messages.ERROR)
            message = 'You cannot delete the only one tag!'
            self.message_user(request, message, level=messages.ERROR)
        else:
            obj.delete()


admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(RecipeTag, RecipeTagAdmin)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)

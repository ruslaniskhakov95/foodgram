from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Доступ для авторов или только чтение."""
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)

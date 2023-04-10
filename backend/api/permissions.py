from rest_framework import permissions


class IsUserAdminOrReadOnly(permissions.BasePermission):
    message = 'Доступ разрешен только админу или пользователю'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (obj.id == request.user or request.user.is_superuser)


class IsOwnerAdminOrReadOnly(permissions.BasePermission):
    message = 'Доступ разрешен только автору или администратору'

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_superuser
                or obj.author == request.user)


class IsAdminOrReadOnly(permissions.BasePermission):
    message = ('Доступ разрешен только админу,'
               'Неавторизованным пользователям разрешён только просмотр.')

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_superuser)

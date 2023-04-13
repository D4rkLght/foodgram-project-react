from rest_framework import permissions


class IsOwnerAdminOrReadOnly(permissions.BasePermission):
    message = 'Доступ разрешен только админу или aвтору'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (obj.author == request.user or request.user.is_superuser)


class IsAdminUserOrReadOnly(permissions.BasePermission):
    message = ('Доступ разрешен админу и авторизованому юзеру,'
               'Неавторизованным пользователям разрешён только просмотр.')

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.id == request.user
                or request.user.is_superuser)

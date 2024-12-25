from rest_framework import permissions


class IsAuthor(permissions.BasePermission):
    """
    Проверка прав доступа к объекту. Пользователь имеет доступ,
    если он является автором объекта.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user

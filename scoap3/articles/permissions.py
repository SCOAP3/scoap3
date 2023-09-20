from rest_framework import permissions


class AdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method == "POST" and not request.user.has_perm(
            "articles.add_article"
        ):
            return False

        return True

    def has_object_permission(self, request, view, obj):
        if request.method in ("PUT", "PATCH") and request.user.has_perm(
            "articles.change_article"
        ):
            return True

        if request.method == "DELETE" and request.user.has_perm(
            "articles.delete_article"
        ):
            return True

        if request.method in permissions.SAFE_METHODS:
            return True

        return False

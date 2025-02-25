from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsSuperUserOrReadOnly(BasePermission):
    """
    Custom permission to only allow superusers to edit objects.
    Read-only access is allowed for other users.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_superuser

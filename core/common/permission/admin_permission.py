from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """
    Custom permission to only allow admin users to access certain views.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated and is an admin
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_superuser or request.user.is_admin)
        )

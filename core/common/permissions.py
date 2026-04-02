from rest_framework.permissions import BasePermission


from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """
    Allow access only to admin or superuser.
    """

    def has_permission(self, request, view):
        user = request.user

        print("Checking IsAdmin permission for user:", user)

        if not user or not user.is_authenticated:
            print("User not authenticated")
            return False

        is_admin = getattr(user, "is_admin", False)

        print("is_superuser:", user.is_superuser)
        print("is_admin:", is_admin)

        return user.is_superuser or is_admin


class IsOrganizationMember(BasePermission):
    """
    Custom permission to only allow organization members to access certain views.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated and is an admin
        return request.user and request.user.is_authenticated and request.user.is_owner

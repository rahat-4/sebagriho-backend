from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """
    Custom manager for User model where the phone number is the unique identifier.
    """

    def create_user(self, phone, password=None, **extra_fields):
        """
        Creates and saves a regular user with the given phone number and password.
        """
        if not phone:
            raise ValueError("The phone number is required")

        # Additional default or extra field handling
        extra_fields.setdefault("is_active", True)

        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given phone number and password.
        """
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_admin", True)

        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")
        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_admin"):
            raise ValueError("Superuser must have is_admin=True.")

        return self.create_user(phone, password, **extra_fields)

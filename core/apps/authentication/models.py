from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)

# from django.core.mail import send_mail
from django.db import models
from django.utils import timezone

from autoslug import AutoSlugField

from phonenumber_field.modelfields import PhoneNumberField


from .choices import BloodGroups, UserGender, UserStatus
from .managers import UserManager
from .utils import get_user_media_path_prefix, get_user_slug

from common.models import BaseModelWithUid


class User(AbstractBaseUser, PermissionsMixin, BaseModelWithUid):
    slug = AutoSlugField(populate_from=get_user_slug, unique=True)
    phone = PhoneNumberField(unique=True)
    email = models.EmailField(max_length=255, unique=True, blank=True, null=True)
    secondary_phone = PhoneNumberField(blank=True, null=True)
    secondary_email = models.EmailField(blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    nid = models.CharField(max_length=20, blank=True, null=True)
    nid_front = models.ImageField(
        upload_to=get_user_media_path_prefix, blank=True, null=True
    )
    nid_back = models.ImageField(
        upload_to=get_user_media_path_prefix, blank=True, null=True
    )
    avatar = models.ImageField(
        "Avatar",
        upload_to=get_user_media_path_prefix,
        blank=True,
        null=True,
    )
    gender = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=UserGender.choices,
        default=UserGender.MALE,
    )
    blood_group = models.CharField(
        max_length=5, choices=BloodGroups.choices, blank=True, null=True
    )
    date_of_birth = models.DateField(blank=True, null=True)
    height = models.FloatField(blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=UserStatus.choices,
        default=UserStatus.ACTIVE,
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_owner = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.get_display_name()

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)
        if self.secondary_email:
            self.secondary_email = self.__class__.objects.normalize_email(
                self.secondary_email
            )

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        return f"{self.first_name or ''} {self.last_name or ''}".strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name or self.get_display_name()

    def get_display_name(self):
        """
        Return the most descriptive name available.
        """
        return self.get_full_name() if self.get_full_name() else str(self.phone)

    def get_organization(self):
        return self.organization_members.get().organization


class RegistrationSession(BaseModelWithUid):
    avatar = models.ImageField(
        "Avatar",
        upload_to=get_user_media_path_prefix,
        blank=True,
        null=True,
    )
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    phone = PhoneNumberField(unique=True)
    email = models.EmailField(max_length=255, unique=True, blank=True, null=True)
    gender = models.CharField(
        max_length=20,
        blank=True,
        choices=UserGender.choices,
        default=UserGender.MALE,
    )
    nid = models.CharField(max_length=20, blank=True, null=True)
    nid_front = models.ImageField(
        upload_to=get_user_media_path_prefix, blank=True, null=True
    )
    nid_back = models.ImageField(
        upload_to=get_user_media_path_prefix, blank=True, null=True
    )
    blood_group = models.CharField(
        max_length=5, choices=BloodGroups.choices, blank=True, null=True
    )
    date_of_birth = models.DateField(blank=True, null=True)
    is_owner = models.BooleanField(default=False)

    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Session expire after 1 hour by default
            self.expires_at = timezone.now() + timezone.timedelta(hours=1)
        super().save(*args, **kwargs)

    def is_expired(self):
        return self.expires_at < timezone.now()

    def is_otp_expired(self):
        if not self.otp_created_at:
            return True

        # OTP expire after 5 minutes
        return timezone.now() > (self.otp_created_at + timezone.timedelta(minutes=5))

from autoslug import AutoSlugField
from phonenumber_field.modelfields import PhoneNumberField

from django.core.exceptions import ValidationError
from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _


from common.models import BaseModelWithUid

from .choices import (
    OrganizationType,
    OrganizationStatus,
    OrganizationMemberStatus,
    AppearanceFontFamilyType,
)
from .utils import (
    get_organization_slug,
    get_organization_media_path_prefix,
    appearance_favicon_upload_path,
    appearance_logo_upload_path,
    validate_subdomain,
)

User = get_user_model()


class Organization(BaseModelWithUid):
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sub_organizations",
    )
    slug = AutoSlugField(unique=True, populate_from="name")
    subdomain = models.CharField(
        max_length=63,
        unique=True,
        validators=[validate_subdomain],
    )
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255, blank=True, null=True)
    logo = models.ImageField(
        upload_to=get_organization_media_path_prefix, blank=True, null=True
    )
    organization_type = models.CharField(
        max_length=25,
        choices=OrganizationType.choices,
        default=OrganizationType.CHAMBER,
    )
    status = models.CharField(
        max_length=25,
        choices=OrganizationStatus.choices,
        default=OrganizationStatus.ACTIVE,
    )
    description = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone = PhoneNumberField(unique=True, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    youtube = models.URLField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["phone"],
                name="unique_non_null_phone",
                condition=~models.Q(phone=None),
            )
        ]

    def __str__(self):
        return f"{self.name} (Slug: {self.slug}) (UID: {self.uid})"


class OrganizationMember(BaseModelWithUid):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="organization_members",
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="members",
    )
    roles = models.ManyToManyField(
        "OrganizationRole",
        blank=True,
        related_name="members",
    )
    status = models.CharField(
        max_length=20,
        choices=OrganizationMemberStatus.choices,
        default=OrganizationMemberStatus.ACTIVE,
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "organization"],
                name="unique_user_per_organization",
            )
        ]

    def __str__(self):
        return f"{self.user.phone} → {self.organization.name}"


class OrganizationRole(BaseModelWithUid):
    name = models.CharField(max_length=100)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="roles",
    )
    is_owner = models.BooleanField(default=False)
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="organization_roles",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "organization"],
                name="unique_role_name_per_organization",
            )
        ]

    def __str__(self):
        return f"{self.organization.name}: {self.name}"


class Appearance(BaseModelWithUid):
    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="appearance_settings",
        verbose_name=_("Organization"),
    )
    about = models.TextField(blank=True, null=True, verbose_name=_("About"))
    site_title = models.CharField(
        max_length=255,
        default="Sebagriho - Connecting Doctors and Patients",
        verbose_name=_("Site Title"),
    )
    logo = models.ImageField(
        upload_to=appearance_logo_upload_path,
        blank=True,
        null=True,
    )
    fav_icon = models.ImageField(
        upload_to=appearance_favicon_upload_path,
        blank=True,
        null=True,
        verbose_name=_("Favicon"),
    )
    primary_color = models.CharField(
        max_length=7,
        default="#308e87",
        verbose_name=_("Primary Color"),
    )
    secondary_color = models.CharField(
        max_length=7,
        default="#f39159",
        verbose_name=_("Secondary Color"),
    )
    font_family = models.CharField(
        max_length=64,
        choices=AppearanceFontFamilyType.choices,
        default=AppearanceFontFamilyType.ROBOTO,
        verbose_name=_("Font Family"),
    )

    class Meta:
        verbose_name = _("Appearance Setting")
        verbose_name_plural = _("Appearance Settings")
        ordering = ["-created_at"]

    def clean(self):
        if self.network and self.organization:
            raise ValidationError(_("Only one of network or organization can be set."))

    def __str__(self):
        if self.organization:
            return f"Appearance Settings for Organization {self.organization.name}"
        return "Appearance Settings"

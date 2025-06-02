from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth import get_user_model

from autoslug import AutoSlugField

from phonenumber_field.modelfields import PhoneNumberField

from common.models import BaseModelWithUid

from .choices import OrganizationType, OrganizationStatus
from .utils import get_organization_slug, get_organization_media_path_prefix

User = get_user_model()


class Organization(BaseModelWithUid):
    slug = AutoSlugField(unique=True, populate_from=get_organization_slug)
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255, blank=True, null=True)
    logo = models.ImageField(
        upload_to=get_organization_media_path_prefix, blank=True, null=True
    )
    subdomain = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        help_text="Required for non-chamber and non-pharmacy organizations",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sub_organizations",
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

    # def clean(self):
    #     super().clean()
    #     # Ensure that subdomain is required for non-chamber and non-pharmacy organizations
    #     if (
    #         self.organization_type
    #         not in (OrganizationType.CHAMBER, OrganizationType.PHARMACY)
    #         and not self.subdomain
    #     ):
    #         raise ValidationError(
    #             {
    #                 "subdomain": "Subdomain is required for non-chamber and non-pharmacy organizations."
    #             }
    #         )

    def save(self, *args, **kwargs):
        self.full_clean()  # Ensure validation before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} (Slug: {self.slug}) (UID: {self.uid})"


class OrganizationMember(BaseModelWithUid):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="organization_members"
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="members"
    )

    def __str__(self):
        return f"{self.user.phone} → {self.organization.name}"


class OrganizationRole(BaseModelWithUid):
    name = models.CharField(max_length=100)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="roles"
    )
    is_owner = models.BooleanField(default=False)
    permissions = models.ManyToManyField(Permission, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "organization"], name="unique_member_per_organization"
            )
        ]

    def __str__(self):
        return f"{self.organization.name}: {self.name}"


class OrganizationPermission(BaseModelWithUid):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="organization_permissions",
    )
    organization_member = models.ForeignKey(
        OrganizationRole,
        on_delete=models.CASCADE,
        related_name="member_permissions",
    )

    class Meta:
        unique_together = ["user", "organization_member"]

    def __str__(self):
        return f"{self.user.phone} → {self.organization_member.name} ({self.organization_member.organization.name})"

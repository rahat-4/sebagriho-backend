from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth import get_user_model

from autoslug import AutoSlugField

from phonenumber_field.modelfields import PhoneNumberField

from common.models import BaseModelWithUid

from .choices import OrganizationType, OrganizationStatus, MethodType
from .utils import get_organization_slug

User = get_user_model()


class Organization(BaseModelWithUid):
    slug = AutoSlugField(unique=True, populate_from=get_organization_slug)
    name = models.CharField(max_length=255)
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
        max_length=20,
        choices=OrganizationType.choices,
        default=OrganizationType.CHAMBER,
    )
    status = models.CharField(
        max_length=20,
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

    def clean(self):
        super().clean()

        # Validate that non-chamber organizations have a subdomain
        if (
            self.organization_type
            not in (OrganizationType.CHAMBER, OrganizationType.PHARMACY)
            and not self.subdomain
        ):
            raise ValidationError(
                {
                    "subdomain": "Subdomain is not required for chamber or pharmacy organizations."
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} (UID: {self.uid})"


class OrganizationRole(BaseModelWithUid):
    name = models.CharField(max_length=100)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="roles"
    )

    class Meta:
        unique_together = ["name", "organization"]

    def __str__(self):
        return f"{self.organization.name} = {self.name}"


class OrganizationMember(BaseModelWithUid):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="members"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="organization_members",
    )
    organization_role = models.ForeignKey(
        OrganizationRole,
        on_delete=models.CASCADE,
        related_name="organization_roles",
    )
    is_owner = models.BooleanField(default=False)

    class Meta:
        unique_together = ["user", "organization"]

    def __str__(self):
        return f"{self.user.phone} - {self.organization.name} ({self.role.name})"


class Permission(BaseModelWithUid):
    organization_role = models.ForeignKey(
        OrganizationRole,
        on_delete=models.CASCADE,
        related_name="permissions",
    )
    methods = models.JSONField(default=list)  # Store multiple methods as a list

    class Meta:
        unique_together = ["organization_role", "methods"]

    def clean(self):
        # Validate that all methods are valid choices
        for method in self.methods:
            if method not in MethodType.values:
                raise ValueError(f"Invalid method: {method}")

    def __str__(self):
        return f"{self.role.name} = {self.methods}"

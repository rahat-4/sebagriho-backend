from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from common.models import BaseModelWithUid

from .choices import OrganizationType, OrganizationStatus

class Organization(BaseModelWithUid):
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    name = models.CharField(max_length=255)
    subdomain = models.SlugField(max_length=255, unique=True, blank=True, null=True, help_text="Required for non-chamber organizations")
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sub_organizations",
    )
    organization_type = models.CharField(
        max_length=20, choices=OrganizationType.choices, default=OrganizationType.CHAMBER
    )
    status = models.CharField(
        max_length=20, choices=OrganizationStatus.choices, default=OrganizationStatus.OPEN
    )
    description = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    contact = models.CharField(max_length=20, blank=True, null=True)
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
        if self.organization_type != OrganizationType.CHAMBER and not self.subdomain:
            raise ValidationError({"subdomain": "Subdomain is required for non-chamber organizations."})
        

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 1
            while Organization.objects.filter(slug=slug).exists():
                count += 1
                slug = f"{base_slug}-{count}"
            self.slug = slug

        if self.organization_type == OrganizationType.CHAMBER:
            self.subdomain = None
        
        self.full_clean()

        super().save(*args, **kwargs)

    def __str__(self):
        if self.organization_type == OrganizationType.CHAMBER:
            return f"{self.name} (UID: {self.uid})"
        
        return f"{self.name} - {self.subdomain} (UID: {self.uid})"


class OrganizationMember(BaseModelWithUid):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey("authentication.User", on_delete=models.CASCADE, related_name="organization_members")
    role = models.ForeignKey("authentication.Role", on_delete=models.CASCADE, related_name="organization_roles")
    is_owner = models.BooleanField(default=False)

    class Meta:
        unique_together = ["user", "organization"]

    def __str__(self):
        return f"{self.user.phone} - {self.organization.name} ({self.role.name})"
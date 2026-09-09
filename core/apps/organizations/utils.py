import re
from django.core.exceptions import ValidationError

RESERVED_SUBDOMAINS = {
    "admin",
    "www",
    "api",
    "mail",
    "ftp",
}


def validate_subdomain(value):
    value = value.strip().lower()

    if value in RESERVED_SUBDOMAINS:
        raise ValidationError(f"'{value}' is a reserved subdomain and cannot be used.")

    if not re.match(r"^[a-z0-9-]+$", value):
        raise ValidationError(
            "Subdomain can only contain lowercase letters, numbers and hyphens."
        )

    if value.startswith("-") or value.endswith("-"):
        raise ValidationError("Subdomain cannot start or end with a hyphen.")

    if len(value) > 63:
        raise ValidationError("Subdomain must be at most 63 characters long.")


def get_organization_slug(instance) -> str:
    return f"{instance.name}-{instance.uid}"


def get_organization_media_path_prefix(instance, filename) -> str:
    return f"organizations/{instance.slug}/{filename}"


def appearance_logo_upload_path(instance, filename) -> str:
    return f"organizations/{instance.organization.slug}/appearance/logo/{filename}"


def appearance_favicon_upload_path(instance, filename) -> str:
    return f"organizations/{instance.organization.slug}/appearance/favicon/{filename}"

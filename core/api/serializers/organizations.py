from rest_framework import serializers

from apps.organizations.models import Organization


class OrganizationProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "uid",
            "slug",
            "name",
            "title",
            "subdomain",
            "logo",
            "organization_type",
            "description",
            "status",
            "phone",
            "email",
            "website",
            "address",
            "facebook",
            "twitter",
            "linkedin",
            "instagram",
            "youtube",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "uid",
            "slug",
            "subdomain",
            "organization_type",
            "logo",
            "status",
            "created_at",
            "updated_at",
        ]

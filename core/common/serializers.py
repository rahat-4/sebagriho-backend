from django.contrib.auth import get_user_model

from rest_framework import serializers

from apps.organizations.models import Organization

from apps.homeopathy.models import HomeopathicMedicine

from .models import Attachment

User = get_user_model()


class UserSlimSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "uid",
            "first_name",
            "last_name",
            "phone",
            "email",
            "gender",
            "nid",
            "nid_front",
            "nid_back",
            "avatar",
            "blood_group",
            "date_of_birth",
            "is_active",
            "is_staff",
            "is_superuser",
            "is_admin",
            "is_owner",
        ]


class AttachmentSimSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = [
            "uid",
            "file",
            "name",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "uid",
            "file",
            "created_at",
            "updated_at",
        ]

    def get_file(self, obj):
        request = self.context.get("request")

        if not obj.file:
            return None

        url = obj.file.url

        if request:
            return request.build_absolute_uri(url)

        return url


class OrganizationSlimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "uid",
            "slug",
            "name",
            "title",
            "logo",
            "subdomain",
            "organization_type",
            "status",
            "address",
            "status",
            "organization_type",
            "phone",
            "email",
            "website",
            "facebook",
            "description",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request")

        if request and representation.get("logo"):
            representation["logo"] = request.build_absolute_uri(representation["logo"])

        return representation


class MedicineSlimSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeopathicMedicine
        fields = [
            "uid",
            "name",
            "power",
            "expiration_date",
            "manufacturer",
            "batch_number",
        ]

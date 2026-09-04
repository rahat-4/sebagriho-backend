from django.contrib.auth import get_user_model
from django.db import transaction

from rest_framework import serializers

from apps.organizations.models import Organization, OrganizationMember, OrganizationRole

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
        ]



class OrganizationSlimSerializers(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "uid",
            "slug",
            "name",
            "parent",
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

class OrganizationOnboardingSerializer(serializers.Serializer):
    user = UserSlimSerializer()
    organization = OrganizationSlimSerializers()

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop("user")
        organization_data = validated_data.pop("organization")

        # 1. Create User
        user = User.objects.create_user(
            password="Test123pass",
            is_owner=True,
            **user_data,
        )

        # 2. Create Organization
        parent_organization_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')} Organization"
        parent_organization = Organization.objects.create(
            name=parent_organization_name,
        )

        organization_data = {
            **organization_data,
            "parent": parent_organization,
        }

        organization = Organization.objects.create(**organization_data)

        # 3. Create Owner Role
        parent_owner_role = OrganizationRole.objects.create(
            name="Owner",
            organization=parent_organization,
            is_owner=True,
        )
        owner_role = OrganizationRole.objects.create(
            name="Owner",
            organization=organization,
            is_owner=True,
        )

        # 4. Create Organization Member
        parent_organization_member = OrganizationMember.objects.create(
            user=user,
            organization=parent_organization,
        )
        member = OrganizationMember.objects.create(
            user=user,
            organization=organization,
        )

        # 5. Assign Owner Role
        member.roles.add(owner_role)
        parent_organization_member.roles.add(parent_owner_role)

        # # 6. Create default appearance
        # Appearance.objects.create(
        #     organization=organization,
        # )

        return {
            "user": user,
            "organization": organization,
            "member": member,
        }


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "uid",
            "slug",
            "name",
            "parent",
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
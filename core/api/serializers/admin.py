from django.contrib.auth import get_user_model
from django.db import transaction

from rest_framework import serializers

from apps.organizations.models import Organization, OrganizationMember, OrganizationRole

User = get_user_model()


class AdminUserOnboardingSerializer(serializers.ModelSerializer):
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


class AdminOrganizationOnboardingDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
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
        ]


class AdminOrganizationMemberSerializer(serializers.ModelSerializer):
    user = AdminUserOnboardingSerializer(read_only=True)
    organization = AdminOrganizationOnboardingDataSerializer(read_only=True)

    class Meta:
        model = OrganizationMember
        fields = [
            "uid",
            "user",
            "organization",
            "status",
            "joined_at",
        ]


class AdminOrganizationOnboardingSerializer(serializers.Serializer):
    user = AdminUserOnboardingSerializer()
    organization = AdminOrganizationOnboardingDataSerializer()

    def validate(self, attrs):
        user_data = attrs.get("user", {})

        phone = user_data.get("phone")
        email = user_data.get("email")

        errors = {}

        if phone and User.objects.filter(phone=phone).exists():
            errors["phone"] = "A user with this phone number already exists."

        if email and User.objects.filter(email__iexact=email).exists():
            errors["email"] = "A user with this email address already exists."

        if errors:
            raise serializers.ValidationError({"user": errors})

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data["user"]
        organization_data = validated_data["organization"]

        # 1. Create user
        user = User.objects.create_user(
            password="Test123pass",
            is_owner=True,
            **user_data,
        )

        # 2. Create parent organization
        first_name = user_data.get("first_name") or ""
        last_name = user_data.get("last_name") or ""

        parent_organization = Organization.objects.create(
            name=f"{first_name} {last_name} Organization".strip()
        )

        # 3. Create child organization
        organization = Organization.objects.create(
            parent=parent_organization,
            **organization_data,
        )

        # 4. Create owner roles
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

        # 5. Create memberships
        parent_member = OrganizationMember.objects.create(
            user=user,
            organization=parent_organization,
        )

        member = OrganizationMember.objects.create(
            user=user,
            organization=organization,
        )

        # 6. Assign roles
        parent_member.roles.add(parent_owner_role)
        member.roles.add(owner_role)

        return member


class AdminOrganizationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
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
        ]


class AdminOrganizationMemberUpdateSerializer(serializers.ModelSerializer):
    organization = AdminOrganizationUpdateSerializer()

    class Meta:
        model = OrganizationMember
        fields = [
            "organization",
            "status",
        ]

    @transaction.atomic
    def update(self, instance, validated_data):
        organization_data = validated_data.pop("organization", None)

        if organization_data:
            organization = instance.organization

            for field, value in organization_data.items():
                setattr(organization, field, value)

            organization.save()

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()

        return instance

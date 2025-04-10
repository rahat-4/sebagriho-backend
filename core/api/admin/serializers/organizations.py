from django.contrib.auth import get_user_model

from rest_framework import serializers

from apps.organizations.models import Organization, OrganizationMember

User = get_user_model()


class OrganizationSlimSerializers(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"


class OrganizationMemberSerializer(serializers.ModelSerializer):
    # user = serializers.SlugRelatedField(
    #     queryset=User.objects.filter(is_active=True),
    #     slug_field="uid",
    #     required=True,
    # )
    organization = OrganizationSlimSerializers()

    class Meta:
        model = OrganizationMember
        fields = "__all__"

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        organization_data = validated_data.pop("organization")
        user = User.objects.create(**user_data)
        organization = Organization.objects.create(**organization_data)
        organization_member = OrganizationMember.objects.create(
            user=user,
            organization=organization,
            **validated_data,
        )
        return organization_member


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"

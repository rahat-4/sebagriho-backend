from django.contrib.auth import get_user_model
from django.db import transaction

from rest_framework import serializers

from apps.authentication.models import RegistrationSession
from apps.organizations.models import Organization, OrganizationMember


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
    status = serializers.SerializerMethodField()
    organization_type = serializers.SerializerMethodField()

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

    def get_status(self, obj):
        return obj.get_status_display()

    def get_organization_type(self, obj):
        return obj.get_organization_type_display()


class OrganizationMemberSerializer(serializers.ModelSerializer):
    session_id = serializers.UUIDField(required=True, write_only=True)
    user = UserSlimSerializer(read_only=True)
    organization = OrganizationSlimSerializers()

    class Meta:
        model = OrganizationMember
        fields = ["uid", "session_id", "user", "organization"]

    def validate(self, attrs):
        session_id = attrs.get("session_id")

        if session_id:
            try:
                registration_session = RegistrationSession.objects.get(uid=session_id)
            except RegistrationSession.DoesNotExist:
                raise serializers.ValidationError({"session_id": "Invalid session ID."})

            if registration_session.is_expired():
                raise serializers.ValidationError(
                    {"session_id": "Registration session expired. Please start over."}
                )

            if not registration_session.is_verified:
                raise serializers.ValidationError(
                    {
                        "session_id": "Phone number is not verified. Please verify your phone number first."
                    }
                )

        return super().validate(attrs)

    def create(self, validated_data):
        with transaction.atomic():
            session_id = validated_data.pop("session_id")
            organization_data = validated_data.pop("organization")

            registration_session = RegistrationSession.objects.filter(
                uid=session_id
            ).first()

            user_data = {
                "avatar": registration_session.avatar,
                "first_name": registration_session.first_name,
                "last_name": registration_session.last_name,
                "phone": registration_session.phone,
                "email": registration_session.email,
                "gender": registration_session.gender,
                "nid": registration_session.nid,
                "nid_front": registration_session.nid_front,
                "nid_back": registration_session.nid_back,
                "is_owner": registration_session.is_owner,
            }

            user = User.objects.create(**user_data)
            organization = Organization.objects.create(**organization_data)
            organization_member = OrganizationMember.objects.create(
                user=user,
                organization=organization,
                **validated_data,
            )
            return organization_member

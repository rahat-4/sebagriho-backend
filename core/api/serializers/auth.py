from rest_framework import serializers

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import get_user_model

from apps.authentication.models import RegistrationSession
from apps.organizations.models import OrganizationMember


User = get_user_model()



class MeSerializer(serializers.ModelSerializer):
    organization_slug = serializers.SerializerMethodField()
    name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = User
        fields = [
            "uid",
            "name",
            "phone",
            "email",
            "gender",
            "nid",
            "nid_front",
            "nid_back",
            "avatar",
            "blood_group",
            "date_of_birth",
            "is_admin",
            "is_owner",
            "is_password_set",
            "organization_slug",
        ]

    def get_organization_slug(self, obj):
        organization_member = OrganizationMember.objects.filter(user=obj).first()
        if organization_member:
            return organization_member.organization.slug
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request")

        def make_absolute(uri):
            return request.build_absolute_uri(uri) if uri and request else uri

        # Convert relative URLs to absolute
        representation["avatar"] = make_absolute(representation.get("avatar"))
        representation["nid_front"] = make_absolute(representation.get("nid_front"))
        representation["nid_back"] = make_absolute(representation.get("nid_back"))

        return representation


class OtpVerificationSerializer(serializers.Serializer):
    session_id = serializers.UUIDField(required=True)
    otp = serializers.CharField(required=True, max_length=6)

    def validate(self, attrs):
        session_id = attrs.get("session_id")
        otp = attrs.get("otp")

        try:
            session = RegistrationSession.objects.get(uid=session_id)
        except RegistrationSession.DoesNotExist:
            raise serializers.ValidationError({"session_id": "Invalid session ID."})

        if session.is_expired():
            raise serializers.ValidationError(
                {"session_id": "Registration session expired. Please start over."}
            )

        if session.is_otp_expired():
            raise serializers.ValidationError(
                {"otp": "OTP expired. Please request a new one."}
            )


        if session.otp != otp:
            raise serializers.ValidationError({"otp": "Invalid OTP. Please try again."})

        self.session = session
        return attrs

    def save(self):
        self.session.is_verified = True
        self.session.save()
        return self.session


class ForgotPasswordSerializer(serializers.Serializer):
    session_id = serializers.UUIDField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Password fields didn't match."}
            )

        try:
            validate_password(attrs["password"])
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": e.messages})

        session_id = attrs.get("session_id")

        try:
            session = RegistrationSession.objects.get(uid=session_id)
        except RegistrationSession.DoesNotExist:
            raise serializers.ValidationError({"session_id": "Invalid session ID."})

        print("Session:", session)

        if session.is_expired():
            raise serializers.ValidationError(
                {"session_id": "Registration session expired. Please start over."}
            )

        if not session.is_verified:
            raise serializers.ValidationError(
                {
                    "session_id": "Phone number is not verified. Please verify your phone number first."
                }
            )

        self.session = session
        return attrs

    def create(self, validated_data):
        password = validated_data.get("password")
        session = self.session

        user = User.objects.filter(phone=session.phone).first()
        if not user:
            raise serializers.ValidationError("User not found.")
        user.set_password(password)
        user.save()

        # Delete the registration session
        session.delete()

        return user


class ResetPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Password fields didn't match."}
            )

        user = self.context["request"].user

        if not user.check_password(attrs["old_password"]):
            raise serializers.ValidationError({"old_password": "Invalid old password."})

        return attrs

    def create(self, validated_data):
        new_password = validated_data.get("new_password")

        user = self.context["request"].user
        user.set_password(new_password)
        user.save()

        return user


class SetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )
    password_confirm = serializers.CharField(
        write_only=True,
    )

    def validate(self, attrs):
        password = attrs["password"]
        password_confirm = attrs["password_confirm"]

        if password != password_confirm:
            raise serializers.ValidationError({
                "password_confirm": "Passwords do not match."
            })

        user = self.context["user"]

        validate_password(password, user=user)

        return attrs

    def save(self, **kwargs):
        user = self.context["user"]

        user.set_password(self.validated_data["password"])
        user.is_password_set = True
        user.save(update_fields=["password", "is_password_set"])

        return user
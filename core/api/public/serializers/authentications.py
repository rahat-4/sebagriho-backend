from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from rest_framework import serializers

from apps.authentication.models import RegistrationSession
from apps.organizations.models import Organization, OrganizationMember
import random
import string
from rest_framework_simplejwt.tokens import RefreshToken
from phonenumber_field.serializerfields import PhoneNumberField


from common.serializers import OrganizationSlimSerializer

User = get_user_model()


class InitialRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrationSession
        fields = [
            "uid",
            "avatar",
            "first_name",
            "last_name",
            "phone",
            "email",
            "gender",
            "nid",
            "nid_front",
            "nid_back",
            "is_owner",
        ]

    # Using for organization and organization's owner registration
    def __init__(self, *args, **kwargs):
        # Remove is_owner field if the user is not a superuser or staff
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            if request.user.is_superuser or request.user.is_staff:
                return
        self.fields.pop("is_owner")

    def validate_phone(self, value):
        # Check if the phone number is already registered
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError(
                "This phone number is already registered."
            )

        # Check if there's an active registration session with the same phone number
        existing_session = RegistrationSession.objects.filter(phone=value).first()

        if existing_session and not existing_session.is_expired():
            # Update the existing session instead of creating a new one
            self.instance = existing_session

        return value

    def validate_email(self, value):
        # Check if the email is already registered
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def create(self, validated_data):
        # Generate OTP
        otp = "".join(random.choices(string.digits, k=6))

        # Create or update the registration session
        if self.instance:
            session = self.instance

            for key, value in validated_data.items():
                setattr(session, key, value)
        else:
            session = RegistrationSession(**validated_data)

        # Set OTP and its creation time
        session.otp = otp
        session.otp_created_at = timezone.now()
        session.is_verified = False
        session.is_owner = True
        session.save()

        # In a real application, send the OTP via SMS here
        print(f"OTP for {session.phone}: {otp}")

        return session


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

        user = User.objects.get(phone=session.phone)
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


class MeSerializer(serializers.ModelSerializer):
    organization = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

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
            "organization",
        ]

    def get_name(self, obj):
        return obj.get_full_name()

    def get_organization(self, obj):
        if obj.is_owner:
            organization = OrganizationMember.objects.get(user=obj).organization
            return OrganizationSlimSerializer(organization, context=self.context).data
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

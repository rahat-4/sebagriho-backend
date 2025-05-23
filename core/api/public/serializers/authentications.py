from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone

from rest_framework import serializers

from apps.authentication.models import RegistrationSession

import random
import string
from rest_framework_simplejwt.tokens import RefreshToken
from phonenumber_field.serializerfields import PhoneNumberField

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


class SetPasswordSerializer(serializers.Serializer):
    session_id = serializers.UUIDField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

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

        # Create the actual user
        user_data = {
            "phone": session.phone,
            "email": session.email,
            "first_name": session.first_name,
            "last_name": session.last_name,
            "gender": session.gender,
            "date_of_birth": session.date_of_birth,
            "blood_group": session.blood_group,
            "is_owner": session.is_owner,
            "password": password,
        }
        user = User.objects.create_user(**user_data)

        # Delete the registration session after successful user creation
        session.delete()

        return user


class UserLoginSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        identifier = attrs.get("identifier")
        password = attrs.get("password")

        user = (
            User.objects.filter(phone=identifier).first()
            or User.objects.filter(email=identifier).first()
        )

        if user is None:
            raise serializers.ValidationError(
                {"identifier": "User with this identifier does not exist."}
            )

        user = authenticate(username=user.phone, password=password)

        if user is None:
            raise serializers.ValidationError({"password": "Password is incorrect."})

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return {"user": user, "refresh": refresh, "access_token": access_token}

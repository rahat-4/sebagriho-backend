import random
import string

from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.models import RegistrationSession
from apps.organizations.models import OrganizationMember, PlatformStaff

from ..serializers.auth import (
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    OtpVerificationSerializer,
    MeSerializer,
    SetPasswordSerializer,
)

User = get_user_model()


class PhoneVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get("phone")
        user = User.objects.filter(phone=phone).first()

        if user:
            # Generate OTP
            otp = "".join(random.choices(string.digits, k=6))
            session, created = RegistrationSession.objects.update_or_create(
                phone=phone,
                defaults={
                    "otp": otp,
                    "otp_created_at": timezone.now(),
                },
            )

            response = {
                "message": "OTP sent to your phone.",
                "session_id": session.uid,
            }
            http_status = status.HTTP_200_OK
        else:
            response = {"message": "User not found."}
            http_status = status.HTTP_404_NOT_FOUND

        return Response(response, status=http_status)


class ForgotPasswordView(CreateAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "Password set successfully.",
                    "uid": user.uid,
                    "slug": user.slug,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "Password reset successfully.",
                    "uid": user.uid,
                    "slug": user.slug,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OtpVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OtpVerificationSerializer(data=request.data)
        if serializer.is_valid():
            session = serializer.save()
            return Response(
                {
                    "message": "OTP verified successfully. You can now set your password.",
                    "session_id": session.uid,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeView(RetrieveUpdateAPIView):
    serializer_class = MeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class LoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        is_platform = getattr(request, "is_platform", False)
        organization = getattr(request, "organization", None)

        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        user = serializer.user

        # --------------------------------
        # Platform login
        # --------------------------------
        if is_platform:
            if not PlatformStaff.objects.filter(
                user=user,
                user__is_active=True,
                is_active=True,
            ).exists():
                return Response(
                    {
                        "error": (
                            "You do not have access to the " "administration portal"
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        # --------------------------------
        # Organization login
        # --------------------------------
        else:
            if not organization:
                return Response(
                    {"error": ("Organization subdomain is required")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not OrganizationMember.objects.filter(
                user=user,
                organization=organization,
                user__is_active=True,
            ).exists():
                return Response(
                    {"error": ("You do not have access to this " "organization")},
                    status=status.HTTP_403_FORBIDDEN,
                )

        data = serializer.validated_data

        data["admin"] = user.is_admin
        data["user_name"] = user.get_full_name()
        data["is_platform"] = is_platform

        if organization:
            data["organization"] = {
                "id": str(organization.uid),
                "name": organization.name,
                "subdomain": organization.subdomain,
            }

        return Response(data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {"error": "Invalid token or token already blacklisted"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "Successfully logged out"},
            status=status.HTTP_205_RESET_CONTENT,
        )


class SetPasswordView(GenericAPIView):
    serializer_class = SetPasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={
                "request": request,
                "user": request.user,
            },
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Password set successfully."},
            status=status.HTTP_200_OK,
        )

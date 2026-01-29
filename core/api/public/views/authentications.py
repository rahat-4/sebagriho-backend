import random
import string
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from apps.authentication.models import RegistrationSession

from common.cookies import set_auth_cookies

from ..serializers.authentications import (
    InitialRegistrationSerializer,
    OtpVerificationSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    MeSerializer,
)

User = get_user_model()

logger = logging.getLogger(__name__)


def is_development():
    return settings.DEBUG


class InitialRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = InitialRegistrationSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            session = serializer.save()
            return Response(
                {
                    "message": "Registration information saved. OTP sent to your phone.",
                    "session_id": session.uid,
                },
                status=status.HTTP_201_CREATED,
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
        serializer = ResetPasswordSerializer(data=request.data)
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


class PhoneVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get("phone")
        user = User.objects.filter(phone=phone).first()

        if user:
            # Generate OTP
            otp = "".join(random.choices(string.digits, k=6))
            initial_registration = RegistrationSession.objects.create(
                phone=phone, otp=otp, otp_created_at=timezone.now()
            )

            response = {
                "message": "OTP sent to your phone.",
                "session_id": initial_registration.uid,
            }
            http_status = status.HTTP_200_OK
        else:
            response = {"message": "User not found."}
            http_status = status.HTTP_404_NOT_FOUND

        return Response(response, status=http_status)


class CookieTokenObtainPairView(TokenObtainPairView):
    """
    Custom login view: issues tokens and sets them in HttpOnly cookies.
    """

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        user = serializer.user

        print("user logged in:", user)
        print("tokens:", data)

        data["admin"] = user.is_admin
        data["user_name"] = user.get_full_name()
        data["organization_uid"] = (
            user.get_organization().uid if user.get_organization() else None
        )

        response = Response(data)

        remember_me = request.data.get("remember_me", False)
        set_auth_cookies(response, data["access"], data["refresh"], remember_me)

        return response


class CookieTokenRefreshView(TokenRefreshView):
    """
    Custom refresh view: refreshes tokens and resets cookies.
    """

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        response = Response(data)

        # Check if remember_me cookie exists from login
        remember_me = request.COOKIES.get("remember_me", False)
        set_auth_cookies(response, data["access"], data["refresh"], remember_me)

        return response


class CookieTokenLogoutView(APIView):
    def post(self, request, *args, **kwargs):
        response = Response({"detail": "Logged out successfully"})
        response.delete_cookie(settings.SIMPLE_JWT["AUTH_COOKIE"])
        response.delete_cookie("refresh_token")
        response.delete_cookie("remember_me")
        return response


class MeView(APIView):
    def get(self, request):
        serializer = MeSerializer(request.user, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserDetailView(APIView):
    def get(self, request, uid):
        user = User.objects.filter(uid=uid).first()
        serializer = MeSerializer(user, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

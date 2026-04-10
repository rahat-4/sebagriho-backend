import random
import string

from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from common.cookies import set_auth_cookies

from apps.authentication.models import RegistrationSession

from ..serializers.auth import (
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    OtpVerificationSerializer,
    InitialRegistrationSerializer,
    MeSerializer,
)

User = get_user_model()


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


class MeView(APIView):
    def get(self, request):
        print("MeView: Current user:", request.user)
        serializer = MeSerializer(request.user, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class CookieTokenLoginView(TokenObtainPairView):
    """
    Custom login view: issues tokens and sets them in HttpOnly cookies.
    """

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        user = serializer.user

        data["admin"] = user.is_admin
        data["user_name"] = user.get_full_name()

        response = Response(data)

        remember_me = request.data.get("remember_me", False)
        set_auth_cookies(response, data["access"], data["refresh"], remember_me)

        return response


class CookieTokenRefreshView(TokenRefreshView):
    """
    Custom refresh view: refreshes tokens and resets cookies.
    """

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            data = serializer.validated_data
            response = Response(data, status=status.HTTP_200_OK)

            remember_me = request.COOKIES.get("remember_me", False)
            set_auth_cookies(response, data["access"], data["refresh"], remember_me)

            return response

        except TokenError:
            return Response(
                {
                    "success": False,
                    "message": "Token is invalid or expired",
                    "code": "token_not_valid",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        except InvalidToken:
            return Response(
                {
                    "success": False,
                    "message": "Invalid refresh token",
                    "code": "invalid_token",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )


class CookieTokenLogoutView(APIView):
    def post(self, request, *args, **kwargs):
        response = Response({"detail": "Logged out successfully"})
        response.delete_cookie(
            settings.SIMPLE_JWT["AUTH_COOKIE"],
            samesite="Lax",
        )
        response.delete_cookie("refresh_token")
        response.delete_cookie("remember_me")
        return response


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

import random
import string

from django.contrib.auth import get_user_model

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from apps.authentication.models import RegistrationSession

from common.utils import unique_number_generator

from ..serializers.authentications import (
    InitialRegistrationSerializer,
    OtpVerificationSerializer,
    SetPasswordSerializer,
    MeSerializer,
)

User = get_user_model()


class InitialRegistration(APIView):
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


class OtpVerification(APIView):
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


class SetPassword(CreateAPIView):
    serializer_class = SetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "User registered successfully.",
                    "uid": user.uid,
                    "slug": user.slug,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPassword(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get("phone")
        user = User.objects.filter(phone=phone).first()

        if user:
            # Generate OTP
            otp = "".join(random.choices(string.digits, k=6))
            initial_registration = RegistrationSession.objects.create(
                phone=phone, otp=otp
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
    def post(self, request, *args, **kwargs):
        phone = request.data.get("phone")
        password = request.data.get("password")
        remember_me = request.data.get("rememberMe") == "true"

        errors = {}

        user = User.objects.filter(phone=phone).first()
        if not user:
            errors["phone"] = ["User not found."]
        elif not user.check_password(password):
            errors["password"] = ["Password is incorrect."]

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            access = response.data.get("access")
            refresh = response.data.get("refresh")

            access_max_age = 60 * 15  # 15 minutes
            refresh_max_age = 60 * 60 * 24  # 1 day

            if remember_me:
                print("Remember me is true")
                access_max_age = 60 * 60 * 24  # 24 hours
                refresh_max_age = 60 * 60 * 24 * 7  # 7 days

                response.set_cookie(
                    key="remember_me",
                    value="true",
                    max_age=refresh_max_age,
                    httponly=False,  # Needs to be readable by JS to conditionally refresh or logout
                    secure=False,
                    samesite="None",
                )

            response.set_cookie(
                key="access_token",
                value=access,
                httponly=True,
                secure=True,  # Secure must be True if samsite=None
                samesite="None",
                max_age=access_max_age,
            )
            response.set_cookie(
                key="refresh_token",
                value=refresh,
                httponly=True,
                secure=True,
                samesite="None",
                max_age=refresh_max_age,
            )

            response.data = {
                "message": "Login successful.",
            }

        return response


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        remember_me = request.COOKIES.get("remember_me") == "true"
        if not refresh_token:
            return Response(
                {"detail": "Refresh token not found."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        request.data["refresh"] = refresh_token
        try:
            response = super().post(request, *args, **kwargs)
        except TokenError as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        if response.status_code == status.HTTP_200_OK:
            access = response.data.get("access")
            refresh = response.data.get("refresh")

            access_max_age = 60 * 15  # 15 minutes
            refresh_max_age = 60 * 60 * 24  # 1 day

            if remember_me == "true":
                access_max_age = 60 * 60 * 24 * 24
                refresh_max_age = 60 * 60 * 24 * 7

            response.set_cookie(
                key="access_token",
                value=access,
                httponly=True,
                secure=False,
                samesite="None",
                max_age=access_max_age,
            )
            response.set_cookie(
                key="refresh_token",
                value=refresh,
                httponly=True,
                secure=False,
                samesite="None",
                max_age=refresh_max_age,
            )

            response.data = {
                "message": "Access token refreshed.",
            }

        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception as e:
            pass

        # Clear cookies
        response = Response({"message": "Logged out."}, status=status.HTTP_200_OK)
        response.delete_cookie("refresh_token")
        response.delete_cookie("access_token")
        response.delete_cookie("remember_me")

        return response


class MeView(APIView):

    def get(self, request):
        serializer = MeSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

import random
import string

from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsAdmin

from apps.authentication.models import RegistrationSession

from ..serializers.auth import (
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    OtpVerificationSerializer,
    InitialRegistrationSerializer,
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

class InitialRegistrationView(APIView):
    permission_classes = [IsAdmin]

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
    
class MeView(APIView):
    def get(self, request):
        serializer = MeSerializer(request.user, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)



class LoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        data = serializer.validated_data
        user = serializer.user

        data["admin"] = user.is_admin
        data["user_name"] = user.get_full_name()

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
            {
                "message": "Password set successfully."
            },
            status=status.HTTP_200_OK,
        )
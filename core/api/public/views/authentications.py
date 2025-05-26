from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from ..serializers.authentications import (
    InitialRegistrationSerializer,
    OtpVerificationSerializer,
    SetPasswordSerializer,
)


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
                    "otp": session.otp,  # Remove this in production
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


class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            access = response.data.get("access")
            refresh = response.data.get("refresh")

            response.set_cookie(
                key="access_token",
                value=access,
                httponly=True,
                secure=False,  # Ensure this is set to True in production
                samesite="None",  # Allow cross-site requests
                max_age=900,  # 15 minutes
            )
            response.set_cookie(
                key="refresh_token",
                value=refresh,
                httponly=True,
                secure=False,
                samesite="None",  # Allow cross-site requests
                max_age=86400,  # 1 day
            )

            response.data = {
                "message": "Login successful.",
            }
            return response


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token not found."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        request.data["refresh"] = refresh_token
        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            access = response.data.get("access")

            response.set_cookie(
                key="access_token",
                value=access,
                httponly=True,
                secure=False,
                samesite="None",  # Allow cross-site requests
                max_age=900,  # 15 minutes
            )
            response.delete_cookie("refresh_token")  # clear old refresh token

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

        return response

from django.urls import path

from ..views.authentications import (
    PhoneVerificationView,
    ForgotPasswordView,
    ResetPasswordView,
    InitialRegistrationView,
    OtpVerificationView,
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    CookieTokenLogoutView,
    MeView,
    UserDetailView,
)


urlpatterns = [
    path(
        "/phone-verification",
        PhoneVerificationView.as_view(),
        name="public.phone-verification",
    ),
    path(
        "/forgot-password", ForgotPasswordView.as_view(), name="public.forgot-password"
    ),
    path("/reset-password", ResetPasswordView.as_view(), name="public.reset-password"),
    path(
        "/otp-verification",
        OtpVerificationView.as_view(),
        name="public.otp-verification",
    ),
    path(
        "/initial-registration",
        InitialRegistrationView.as_view(),
        name="public.initial-registration",
    ),
    path("/token/refresh", CookieTokenRefreshView.as_view(), name="token-refresh"),
    path("/logout", CookieTokenLogoutView.as_view(), name="logout"),
    path("/login", CookieTokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("/user-detail/<uuid:uid>", UserDetailView.as_view(), name="user-detail"),
    path("/me", MeView.as_view(), name="me"),
]

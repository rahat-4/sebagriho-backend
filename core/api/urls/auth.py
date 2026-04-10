from django.urls import path

from ..views.auth import (
    CookieTokenLoginView,
    CookieTokenRefreshView,
    CookieTokenLogoutView,
    ForgotPasswordView,
    ResetPasswordView,
    PhoneVerificationView,
    OtpVerificationView,
    InitialRegistrationView,
    MeView,
)

urlpatterns = [
    path(
        "/initial-registration",
        InitialRegistrationView.as_view(),
        name="public.initial-registration",
    ),
    path(
        "/phone-verification",
        PhoneVerificationView.as_view(),
        name="auth.phone-verification",
    ),
    path(
        "/otp-verification",
        OtpVerificationView.as_view(),
        name="auth.otp-verification",
    ),
    path("/me", MeView.as_view(), name="me"),
    path("/login", CookieTokenLoginView.as_view(), name="auth.token-login"),
    path("/refresh", CookieTokenRefreshView.as_view(), name="auth.token-refresh"),
    path("/logout", CookieTokenLogoutView.as_view(), name="auth.token-logout"),
    path("/forgot-password", ForgotPasswordView.as_view(), name="auth.forgot-password"),
    path("/reset-password", ResetPasswordView.as_view(), name="auth.reset-password"),
]

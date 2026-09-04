from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from ..views.auth import (
    ForgotPasswordView,
    ResetPasswordView,
    PhoneVerificationView,
    OtpVerificationView,
    MeView,
    LogoutView,
    LoginView,
    SetPasswordView
)

urlpatterns = [
    path(
        "/phone-verification",
        PhoneVerificationView.as_view(),
        name="auth.phone-verification",
    ),
    path("/forgot-password", ForgotPasswordView.as_view(), name="auth.forgot-password"),
    path(
        "/otp-verification",
        OtpVerificationView.as_view(),
        name="auth.otp-verification",
    ),
    
    path("/reset-password", ResetPasswordView.as_view(), name="auth.reset-password"),
    path("/set-password", SetPasswordView.as_view(), name="auth.set-password"),
    path("/me", MeView.as_view(), name="me"),
    path("/logout", LogoutView.as_view(), name="auth.logout"),
    path("/refresh", TokenRefreshView.as_view(), name="auth.token-refresh"),
    path("/login", LoginView.as_view(), name="auth.login"),
]

from django.urls import path

from ..views.authentications import (
    ForgotPassword,
    SetPassword,
    InitialRegistration,
    OtpVerification,
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    LogoutView,
    MeView,
)


urlpatterns = [
    path("/forgot-password", ForgotPassword.as_view(), name="public.forget-password"),
    path("/set-password", SetPassword.as_view(), name="public.set-password"),
    path(
        "/otp-verification",
        OtpVerification.as_view(),
        name="public.otp-verification",
    ),
    path(
        "/initial-registration",
        InitialRegistration.as_view(),
        name="public.initial-registration",
    ),
    path("/token/refresh", CookieTokenRefreshView.as_view(), name="token-refresh"),
    path("/logout", LogoutView.as_view(), name="ogout"),
    path("/login", CookieTokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("/me", MeView.as_view(), name="me"),
]

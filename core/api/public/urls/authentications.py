from django.urls import path

from ..views.authentications import (
    SetPassword,
    UserLogin,
    InitialRegistration,
    OtpVerification,
)

urlpatterns = [
    path("/login", UserLogin.as_view(), name="public.user-login"),
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
]

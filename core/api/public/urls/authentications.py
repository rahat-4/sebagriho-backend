from django.urls import path

from ..views.authentications import (
    SetPassword,
    InitialRegistration,
    OtpVerification,
)

urlpatterns = [
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

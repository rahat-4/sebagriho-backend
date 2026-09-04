from django.urls import path

from ..views.organizations import OrganizationOnboardingView

urlpatterns = [
    path(
    "/onboard",
    OrganizationOnboardingView.as_view(),
),
]

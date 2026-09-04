from django.urls import path

from ..views.organizations import (
    OrganizationOnboardView,
    OrganizationOnboardDetailView,
    OrganizationProfileView,
)

urlpatterns = [
    path("", OrganizationOnboardView.as_view()),
    path("/<uuid:onboard_uid>", OrganizationOnboardDetailView.as_view()),
    path("/<slug:organization_slug>/profile", OrganizationProfileView.as_view()),
]

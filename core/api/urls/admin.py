from django.urls import path

from ..views.admin import (
    AdminOrganizationOnboardListView,
    AdminOrganizationOnboardDetailView,
)

urlpatterns = [
    path("/organization-onboard", AdminOrganizationOnboardListView.as_view()),
    path(
        "/organization-onboard/<uuid:onboard_uid>",
        AdminOrganizationOnboardDetailView.as_view(),
    ),
]

from django.urls import path

from ..views.organizations import OrganizationOnboardView, OrganizationOnboardDetailView

urlpatterns = [
    path(
    "",
    OrganizationOnboardView.as_view()
    ),
    path(
        "/<uuid:onboard_uid>",
        OrganizationOnboardDetailView.as_view()
    ),
]

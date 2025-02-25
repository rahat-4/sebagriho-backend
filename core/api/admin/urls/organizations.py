from django.urls import path

from ..views.organizations import (
    OrganizationMemberListCreateView,
    OrganizationMemberRetrieveUpdateDestroyView,
)

urlpatterns = [
    path(
        "/<uuid:uid>",
        OrganizationMemberRetrieveUpdateDestroyView.as_view(),
        name="organization-retrieve-update-destroy",
    ),
    path(
        "",
        OrganizationMemberListCreateView.as_view(),
        name="organization-list-create",
    ),
]

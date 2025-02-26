from django.urls import path

from ..views.organizations import (
    OrganizationMemberListCreate,
    OrganizationMemberRetrieveUpdateDestroy,
)

urlpatterns = [
    path(
        "/<uuid:organization_member_uid>",
        OrganizationMemberRetrieveUpdateDestroy.as_view(),
        name="admin.organization-retrieve-update-destroy",
    ),
    path(
        "",
        OrganizationMemberListCreate.as_view(),
        name="admin.organization-list-create",
    ),
]

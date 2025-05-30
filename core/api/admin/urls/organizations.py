from django.urls import path

from ..views.organizations import (
    OrganizationListView,
    OrganizationMemberListCreate,
    OrganizationMemberRetrieveUpdateDestroy,
)

urlpatterns = [
    path(
        "/members/<uuid:organization_member_uid>",
        OrganizationMemberRetrieveUpdateDestroy.as_view(),
        name="admin.organizationmember-retrieve-update-destroy",
    ),
    path(
        "/members",
        OrganizationMemberListCreate.as_view(),
        name="admin.organizationmember-list-create",
    ),
    path(
        "",
        OrganizationListView.as_view(),
        name="admin.organization-list-create",
    ),
]

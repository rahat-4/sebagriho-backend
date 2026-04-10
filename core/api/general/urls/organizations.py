from ..views.organizations import (
    OrganizationList,
    OrganizationDetail,
    OrganizationDoctorsList,
    OrganizationDoctorsDetail,
)

from django.urls import path

urlpatterns = [
    path(
        "/<slug:organization_slug>/doctors/<uuid:doctor_uid>",
        OrganizationDoctorsDetail.as_view(),
        name="organization.doctors-detail",
    ),
    path(
        "/<slug:organization_slug>/doctors",
        OrganizationDoctorsList.as_view(),
        name="organization.doctors-list",
    ),
    # Get organization's detail, update and soft delete
    path(
        "/<slug:organization_slug>",
        OrganizationDetail.as_view(),
        name="organization-detail",
    ),
    # Organization add and get list
    path("", OrganizationList.as_view(), name="organization-list"),
]

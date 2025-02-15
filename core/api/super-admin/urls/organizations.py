from ..views.organizations import (
    OrganizationList,
    OrganizationDetail,
    OrganizationDoctorsList,
    OrganizationDoctorsDetail,
)

from django.urls import path

urlpatterns = [
    path(
        "/<uuid:organization_uid>/doctors/<uuid:doctor_uid>",
        OrganizationDoctorsDetail.as_view(),
        name="organization.doctors-detail",
    ),
    path(
        "/<uuid:organization_uid>/doctors",
        OrganizationDoctorsList.as_view(),
        name="organization.doctors-list",
    ),
    path(
        "/<uuid:organization_uid>",
        OrganizationDetail.as_view(),
        name="organization-detail",
    ),
    path("", OrganizationList.as_view(), name="organization-list"),
]

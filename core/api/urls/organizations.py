from django.urls import include, path

from ..views.organizations import OrganizationProfileView

urlpatterns = [
    path("/<slug:organization_slug>/profile", OrganizationProfileView.as_view()),
    path("/<slug:organization_slug>/homeopathy", include("api.urls.homeopathy")),
]

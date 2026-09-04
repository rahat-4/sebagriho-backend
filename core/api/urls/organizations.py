from django.urls import path

from ..views.organizations import OrganizationProfileView

urlpatterns = [
    path("/<slug:organization_slug>/profile", OrganizationProfileView.as_view()),
]

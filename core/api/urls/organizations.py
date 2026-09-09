from django.urls import include, path

from ..views.organizations import OrganizationProfileView

urlpatterns = [
    path("/profile", OrganizationProfileView.as_view()),
]

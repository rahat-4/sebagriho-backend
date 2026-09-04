from django.urls import path

from ..views.organizations import OrganizationListView

urlpatterns = [
    path(
    "",
    OrganizationListView.as_view()
    ),
]

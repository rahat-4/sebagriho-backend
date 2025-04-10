from django.urls import path, include

urlpatterns = [
    path("/organizations", include("api.admin.urls.organizations")),
]

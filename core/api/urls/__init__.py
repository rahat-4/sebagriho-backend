from django.urls import path, include

urlpatterns = [
    path("/organizations", include("api.super-admin.urls.organizations")),
]

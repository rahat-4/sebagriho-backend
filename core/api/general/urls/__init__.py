from django.urls import path, include

urlpatterns = [
    path("/organizations", include("api.urls.organizations")),
]

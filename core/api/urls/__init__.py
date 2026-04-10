from django.urls import include, path

urlpatterns = [
    path("/auth", include("api.urls.auth")),
    path("/admin", include("api.urls.admin")),
    path("/organizations", include("api.urls.organizations")),
]

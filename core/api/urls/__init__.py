from django.urls import include, path

urlpatterns = [
    path("/auth", include("api.urls.auth")),
    path("/organizations", include("api.urls.organizations")),
    path("/admin", include("api.urls.admin")),
]

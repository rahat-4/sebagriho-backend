from django.urls import path, include

urlpatterns = [
    path("/doctors", include("api.admin.urls.doctors")),
    path("/organizations", include("api.admin.urls.organizations")),
]

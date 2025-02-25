from django.urls import path, include

urlpatterns = [
    path("/doctors", include("api.superadmin.urls.doctors")),
    path("/organizations", include("api.superadmin.urls.organizations")),
]

from django.urls import include, path

urlpatterns = [
    path("/homeopathy", include("api.organization.urls.homeopathy")),
]

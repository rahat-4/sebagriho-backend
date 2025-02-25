from django.urls import include, path

urlpatterns = [
    path("/auth", include("api.public.urls.authentications")),
]

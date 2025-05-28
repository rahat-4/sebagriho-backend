from django.contrib import admin
from django.urls import path, include

from api.public.views.authentications import (
    CookieTokenObtainPairView,
    LogoutView,
    CookieTokenRefreshView,
)

urlpatterns = [
    path("super-admin/", admin.site.urls),
    # path("api-auth/", include("rest_framework.urls")),
    # base urls
    path("api/admin", include("api.admin.urls")),
    path("api/public", include("api.public.urls")),
    path("api/organization", include("api.organization.urls")),
]

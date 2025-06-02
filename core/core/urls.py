from django.conf import settings
from django.contrib import admin
from django.urls import path, include

from django.conf.urls.static import static

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

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

from django.http import JsonResponse

from apps.organizations.models import Organization


class SubdomainMiddleware:
    PUBLIC_PATH_PREFIXES = [
        "/super-admin/",
        "/static/",
        "/media/",
        "/auth/set-password",
        "/auth/reset-password",
        "/auth/forgot-password",
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        subdomain = request.headers.get("X-ORGANIZATION-SUBDOMAIN", "").strip().lower()

        # --------------------------------
        # Platform admin
        # --------------------------------
        if subdomain == "admin":
            request.is_platform = True
            request.organization = None
            request.subdomain = subdomain

            return self.get_response(request)

        # --------------------------------
        # Public paths
        # No organization subdomain required
        # --------------------------------
        if any(path.startswith(prefix) for prefix in self.PUBLIC_PATH_PREFIXES):
            request.is_platform = False
            request.organization = None
            request.subdomain = subdomain

            return self.get_response(request)

        # --------------------------------
        # Organization subdomain required
        # --------------------------------
        if not subdomain:
            return JsonResponse(
                {"error": "Organization subdomain is required"},
                status=400,
            )

        # --------------------------------
        # Resolve organization
        # --------------------------------
        try:
            organization = Organization.objects.get(subdomain=subdomain)
        except Organization.DoesNotExist:
            return JsonResponse(
                {"error": "Organization not found"},
                status=404,
            )

        request.is_platform = False
        request.organization = organization
        request.subdomain = subdomain

        return self.get_response(request)

from django.http import JsonResponse

from apps.organizations.models import Organization


class SubdomainMiddleware:
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
        # Super admin API
        # --------------------------------
        if path.startswith("/super-admin/"):
            request.is_platform = True
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

from django.http import JsonResponse

from apps.organizations.models import Organization


class SubdomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        subdomain = request.headers.get("X-ORGANIZATION-SUBDOMAIN", "")

        if subdomain:
            try:
                organization = Organization.objects.get(subdomain=subdomain)
                request.organization = organization
                request.subdomain = subdomain
            except Organization.DoesNotExist:
                return JsonResponse({"error": "Organization not found"}, status=404)

        response = self.get_response(request)
        return response

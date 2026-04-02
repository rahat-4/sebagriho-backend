import re

from django.http import HttpResponseRedirect, JsonResponse

from apps.organizations.models import Organization


class SubdomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(":")[0]  # Remove port if present
        subdomain_pattern = re.compile(r"^(?P<subdomain>[^.]+)\.example\.com$")
        match = subdomain_pattern.match(host)

        if match:
            subdomain = match.group("subdomain")
            try:
                organization = Organization.objects.get(subdomain=subdomain)
                request.organization = organization
                request.subdomain = subdomain
            except Organization.DoesNotExist:
                return JsonResponse({"error": "Organization not found"}, status=404)
        # else:
        #     return HttpResponseRedirect("https://www.example.com")

        response = self.get_response(request)
        return response

from rest_framework.generics import RetrieveUpdateAPIView

from common.permissions import IsOrganizationOwner

from apps.organizations.models import Organization

from ..serializers.organizations import OrganizationProfileSerializer


class OrganizationProfileView(RetrieveUpdateAPIView):
    serializer_class = OrganizationProfileSerializer
    permission_classes = [IsOrganizationOwner]
    lookup_field = "slug"
    lookup_url_kwarg = "organization_slug"

    def get_object(self):
        organization_slug = self.kwargs.get("organization_slug")
        return Organization.objects.get(slug=organization_slug)

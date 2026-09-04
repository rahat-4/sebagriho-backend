from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView

from common.permissions import IsAdmin, IsOrganizationOwner

from apps.organizations.models import Organization, OrganizationMember

from ..serializers.organizations import OrganizationOnboardingSerializer, OrganizationMemberSerializer, OrganizationMemberUpdateSerializer, OrganizationProfileSerializer



class OrganizationOnboardView(ListCreateAPIView):
    permission_classes = [IsAdmin]
    
    def get_serializer_class(self):
        if self.request.method == "POST":
            return OrganizationOnboardingSerializer

        return OrganizationMemberSerializer

    def get_queryset(self):
        return (
            OrganizationMember.objects
            .filter(
                organization__parent__isnull=False,
            )
            .select_related(
                "user",
                "organization",
                "organization__parent",
            )
            .prefetch_related(
                "roles",
            )
        )

class OrganizationOnboardDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]
    lookup_field = "uid"
    lookup_url_kwarg = "onboard_uid"

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return OrganizationMemberUpdateSerializer

        return OrganizationMemberSerializer

    def get_queryset(self):
        return (
            OrganizationMember.objects
            .filter(
                organization__parent__isnull=False,
            )
            .select_related(
                "user",
                "organization",
                "organization__parent",
            )
            .prefetch_related("roles")
        )


class OrganizationProfileView(RetrieveUpdateAPIView):
    serializer_class = OrganizationProfileSerializer
    permission_classes = [IsOrganizationOwner]
    lookup_field = "slug"
    lookup_url_kwarg = "organization_slug"

    def get_object(self):
        organization_slug = self.kwargs.get("organization_slug")
        return Organization.objects.get(slug=organization_slug)
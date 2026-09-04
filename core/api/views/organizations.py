from rest_framework.generics import ListCreateAPIView

from common.permissions import IsAdmin, IsOrganizationOwner

from apps.organizations.models import Organization

from ..serializers.organizations import OrganizationOnboardingSerializer, OrganizationSerializer



class OrganizationListView(ListCreateAPIView):
    permission_classes = [IsAdmin | IsOrganizationOwner]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OrganizationOnboardingSerializer

        return OrganizationSerializer

    def get_queryset(self):
        user = self.request.user

        # Admin: see all child organizations
        if user.is_admin:
            return (
                Organization.objects
                .filter(parent__isnull=False)
                .select_related("parent")
            )

        # Organization owner: see their child organizations
        owner_membership = (
            user.organization_members
            .filter(
                organization__parent__isnull=True,
                roles__is_owner=True,
            )
            .select_related("organization")
            .first()
        )

        if not owner_membership:
            return Organization.objects.none()

        return Organization.objects.filter(
            parent=owner_membership.organization
        )
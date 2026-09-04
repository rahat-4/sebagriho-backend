from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from common.permissions import IsAdmin, IsOrganizationOwner

from apps.organizations.models import OrganizationMember

from ..serializers.organizations import OrganizationOnboardingSerializer, OrganizationMemberSerializer, OrganizationMemberUpdateSerializer



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
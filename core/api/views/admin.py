from django.db import transaction

from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)

from common.permissions import IsAdmin

from apps.organizations.models import OrganizationMember

from ..serializers.admin import (
    AdminOrganizationOnboardingSerializer,
    AdminOrganizationMemberSerializer,
    AdminOrganizationMemberUpdateSerializer,
)


class AdminOrganizationOnboardListView(ListCreateAPIView):
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AdminOrganizationOnboardingSerializer

        return AdminOrganizationMemberSerializer

    def get_queryset(self):
        return (
            OrganizationMember.objects.filter()
            .select_related(
                "user",
                "organization",
            )
            .prefetch_related(
                "roles",
            )
        ).order_by("-created_at")


class AdminOrganizationOnboardDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]
    lookup_field = "uid"
    lookup_url_kwarg = "onboard_uid"

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return AdminOrganizationMemberUpdateSerializer

        return AdminOrganizationMemberSerializer

    def get_queryset(self):
        return (
            OrganizationMember.objects.filter()
            .select_related(
                "user",
                "organization",
            )
            .prefetch_related("roles")
        )

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.user.delete()  # Delete the user associated with the organization member
            instance.organization.delete()  # Delete the organization associated with the organization member
            instance.organization.parent.delete()  # Delete the parent organization associated with the organization member
            instance.roles.clear()  # Clear the roles associated with the organization member

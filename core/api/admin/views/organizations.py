from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.exceptions import ValidationError

from apps.organizations.models import Organization, OrganizationMember
from apps.organizations.choices import OrganizationStatus

from ..serializers.organizations import (
    OrganizationSlimSerializers,
    OrganizationMemberSerializer,
)


class OrganizationListCreate(ListCreateAPIView):
    queryset = Organization.objects.filter()
    serializer_class = OrganizationSlimSerializers


class OrganizationMemberListCreate(ListCreateAPIView):
    queryset = OrganizationMember.objects.all()
    serializer_class = OrganizationMemberSerializer


class OrganizationMemberRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    queryset = OrganizationMember.objects.all()
    serializer_class = OrganizationMemberSerializer

    def get_object(self):
        organization_member_uid = self.kwargs.get("organization_member_uid")

        organization = OrganizationMember.objects.filter(
            uid=organization_member_uid
        ).first()

        if not organization:
            raise ValidationError("Organization member not found!")

        return organization

    def perform_destroy(self, instance):
        instance.organization.status = OrganizationStatus.DELETED
        instance.save()

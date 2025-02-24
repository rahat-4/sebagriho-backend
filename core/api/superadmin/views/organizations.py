from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from apps.organizations.models import Organization, OrganizationMember
from apps.organizations.choices import OrganizationStatus

from ..serializers.organizations import OrganizationMemberSerializer


class OrganizationMemberListCreateView(ListCreateAPIView):
    queryset = OrganizationMember.objects.all()
    serializer_class = OrganizationMemberSerializer


class OrganizationMemberRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = OrganizationMember.objects.all()
    serializer_class = OrganizationMemberSerializer

    def perform_destroy(self, instance):
        instance.organization.status = OrganizationStatus.DELETED
        instance.save()

from rest_framework.generics import RetrieveUpdateAPIView

from common.permissions import IsOrganizationOwner

from ..serializers.organizations import OrganizationProfileSerializer


class OrganizationProfileView(RetrieveUpdateAPIView):
    serializer_class = OrganizationProfileSerializer
    permission_classes = [IsOrganizationOwner]

    def get_object(self):
        return self.request.organization

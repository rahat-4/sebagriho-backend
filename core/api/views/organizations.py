from rest_framework.generics import CreateAPIView

from common.permissions import IsAdmin

from ..serializers.organizations import OrganizationOnboardingSerializer

class OrganizationOnboardingView(CreateAPIView):
    serializer_class = OrganizationOnboardingSerializer
    permission_classes = [IsAdmin] 
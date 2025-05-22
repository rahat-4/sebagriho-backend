from rest_framework.generics import ListCreateAPIView

from apps.patients.models import Patient

from ..serializers.homeopathy import HomeopathyPatientSerializer


class HomeopathyPatientListView(ListCreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = HomeopathyPatientSerializer
    permission_classes = []

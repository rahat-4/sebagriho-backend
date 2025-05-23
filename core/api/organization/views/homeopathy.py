from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from apps.patients.models import Patient

from ..serializers.homeopathy import (
    HomeopathyPatientListSerializer,
    HomeopathyPatientDetailSerializer,
)


class HomeopathyPatientListView(ListCreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = HomeopathyPatientListSerializer
    permission_classes = []


class HomeopathyPatientDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = HomeopathyPatientDetailSerializer
    permission_classes = []

    def get_object(self):
        serial_number = self.kwargs.get("serial_number")
        return self.queryset.get(serial_number=serial_number)

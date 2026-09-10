from rest_framework.generics import ListAPIView

from apps.authentication.choices import UserStatus
from apps.homeopathy.models import HomeopathicPatient, HomeopathicMedicine
from apps.homeopathy.choices import HomeopathicPatientStatus, HomeopathicMedicineStatus

from ..serializers.filters import (
    HomeopathicPatientFilterSerializer,
    HomeopathicMedicineFilterSerializer,
)


class HomeopathicPatientFilterView(ListAPIView):
    serializer_class = HomeopathicPatientFilterSerializer
    pagination_class = None
    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__phone",
        "user__email",
        "serial_number",
        "old_serial_number",
    ]

    def get_queryset(self):
        organization = self.request.organization

        if not organization:
            return HomeopathicPatient.objects.none()

        return HomeopathicPatient.objects.filter(
            organization=organization,
            user__status=UserStatus.ACTIVE,
            status=HomeopathicPatientStatus.ACTIVE,
        ).select_related("user")


class HomeopathicMedicineFilterView(ListAPIView):
    serializer_class = HomeopathicMedicineFilterSerializer
    pagination_class = None
    search_fields = [
        "name",
        "manufacturer",
        "batch_number",
    ]

    def get_queryset(self):
        organization = self.request.organization

        if not organization:
            return HomeopathicMedicine.objects.none()

        return HomeopathicMedicine.objects.filter(
            organization=organization,
            status=HomeopathicMedicineStatus.AVAILABLE,
        )

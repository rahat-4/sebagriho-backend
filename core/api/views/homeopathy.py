from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from apps.homeopathy.models import (
    HomeopathicPatient,
    HomeopathicMedicine,
    HomeopathicAppointment,
)

from common.permissions import IsOrganizationOwner

from ..serializers.homeopathy import (
    HomeopathicPatientSerializer,
    HomeopathicAppointmentSerializer,
    HomeopathicMedicineSerializer,
)


class HomeopathicPatientListCreateView(ListCreateAPIView):
    serializer_class = HomeopathicPatientSerializer
    permission_classes = [IsOrganizationOwner]
    filterset_fields = ["status", "miasm_type"]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__phone",
        "user__email",
        "serial_number",
        "old_serial_number",
    ]

    def get_queryset(self):
        organization = getattr(self.request, "organization", None)

        return (
            HomeopathicPatient.objects.filter(
                organization=organization,
            )
            .select_related("user")
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        serializer.save()


class HomeopathicPatientDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = HomeopathicPatientSerializer
    permission_classes = [IsOrganizationOwner]
    lookup_field = "uid"
    lookup_url_kwarg = "patient_uid"

    def get_queryset(self):
        organization = getattr(self.request, "organization", None)

        return HomeopathicPatient.objects.filter(
            organization=organization,
        ).select_related("user")


class HomeopathicAppointmentListCreateView(ListCreateAPIView):
    permission_classes = [IsOrganizationOwner]
    serializer_class = HomeopathicAppointmentSerializer
    filterset_fields = ["status", "homeopathic_patient__miasm_type"]
    search_fields = [
        "symptoms",
        "homeopathic_patient__user__first_name",
        "homeopathic_patient__user__last_name",
        "homeopathic_patient__user__phone",
        "homeopathic_patient__user__email",
        "homeopathic_patient__serial_number",
        "homeopathic_patient__old_serial_number",
        "homeopathic_patient__relative_phone",
        "homeopathic_patient__age",
    ]

    def get_queryset(self):
        organization = getattr(self.request, "organization", None)
        return (
            HomeopathicAppointment.objects.filter(
                organization=organization,
            )
            .select_related(
                "homeopathic_patient",
                "homeopathic_patient__user",
            )
            .prefetch_related(
                "medicines",
                "attachments",
            )
            .order_by("-created_at")
        )


class HomeopathicAppointmentDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOrganizationOwner]
    serializer_class = HomeopathicAppointmentSerializer

    lookup_field = "uid"
    lookup_url_kwarg = "appointment_uid"

    def get_queryset(self):
        organization = getattr(self.request, "organization", None)
        return (
            HomeopathicAppointment.objects.filter(
                organization=organization,
            )
            .select_related(
                "homeopathic_patient",
                "homeopathic_patient__user",
            )
            .prefetch_related(
                "medicines",
                "attachments",
            )
        )


class HomeopathicMedicineListCreateView(ListCreateAPIView):
    serializer_class = HomeopathicMedicineSerializer
    permission_classes = [IsOrganizationOwner]
    filterset_fields = {
        "status": ["exact"],
        "expiration_date": ["gte", "lte"],
    }
    search_fields = ["name", "manufacturer", "batch_number"]

    def get_queryset(self):
        organization = getattr(self.request, "organization", None)
        return (
            HomeopathicMedicine.objects.filter(
                organization=organization,
            )
            .prefetch_related("attachments")
            .order_by("-created_at")
        )


class HomeopathicMedicineDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = HomeopathicMedicineSerializer
    permission_classes = [IsOrganizationOwner]

    lookup_field = "uid"
    lookup_url_kwarg = "medicine_uid"

    def get_queryset(self):
        organization = getattr(self.request, "organization", None)

        return HomeopathicMedicine.objects.filter(
            organization=organization,
        ).prefetch_related("attachments")

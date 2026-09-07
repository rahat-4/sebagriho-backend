from django.shortcuts import get_object_or_404

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from apps.homeopathy.models import (
    HomeopathicPatient,
    HomeopathicMedicine,
    HomeopathicAppointment,
)
from apps.organizations.models import Organization

from common.permissions import IsOrganizationOwner

from ..serializers.homeopathy import (
    HomeopathicPatientSerializer,
    HomeopathicAppointmentSerializer,
    HomeopathicMedicineSerializer,
)


class HomeopathicPatientListCreateView(ListCreateAPIView):
    serializer_class = HomeopathicPatientSerializer
    permission_classes = [IsOrganizationOwner]

    def get_organization(self):
        return get_object_or_404(
            Organization,
            slug=self.kwargs["organization_slug"],
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["organization"] = self.get_organization()
        return context

    def get_queryset(self):
        return (
            HomeopathicPatient.objects.filter(
                organization=self.get_organization(),
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

    def get_organization(self):
        return get_object_or_404(
            Organization,
            slug=self.kwargs["organization_slug"],
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["organization"] = self.get_organization()
        return context

    def get_queryset(self):
        return HomeopathicPatient.objects.filter(
            organization=self.get_organization(),
        ).select_related("user")


class HomeopathicAppointmentListCreateView(ListCreateAPIView):
    permission_classes = [IsOrganizationOwner]
    serializer_class = HomeopathicAppointmentSerializer

    def get_organization(self):
        return get_object_or_404(
            Organization,
            slug=self.kwargs["organization_slug"],
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["organization"] = self.get_organization()
        return context

    def get_queryset(self):
        return (
            HomeopathicAppointment.objects.filter(
                organization=self.get_organization(),
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

    def get_organization(self):
        return get_object_or_404(
            Organization,
            slug=self.kwargs["organization_slug"],
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["organization"] = self.get_organization()
        return context

    def get_queryset(self):
        return (
            HomeopathicAppointment.objects.filter(
                organization=self.get_organization(),
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

    def get_organization(self):
        return get_object_or_404(
            Organization,
            slug=self.kwargs["organization_slug"],
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["organization"] = self.get_organization()
        return context

    def get_queryset(self):
        return (
            HomeopathicMedicine.objects.filter(
                organization=self.get_organization(),
            )
            .prefetch_related("attachments")
            .order_by("-created_at")
        )


class HomeopathicMedicineDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = HomeopathicMedicineSerializer
    permission_classes = [IsOrganizationOwner]

    lookup_field = "uid"
    lookup_url_kwarg = "medicine_uid"

    def get_organization(self):
        return get_object_or_404(
            Organization,
            slug=self.kwargs["organization_slug"],
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["organization"] = self.get_organization()
        return context

    def get_queryset(self):
        return HomeopathicMedicine.objects.filter(
            organization=self.get_organization(),
        ).prefetch_related("attachments")

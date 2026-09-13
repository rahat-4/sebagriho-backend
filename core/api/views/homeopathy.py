from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.homeopathy.models import (
    HomeopathicPatient,
    HomeopathicMedicine,
    HomeopathicAppointment,
    HomeopathicPrescription,
)

from common.permissions import IsOrganizationOwner

from ..serializers.homeopathy import (
    HomeopathicDashboardSerializer,
    HomeopathicPatientSerializer,
    HomeopathicAppointmentSerializer,
    HomeopathicMedicineSerializer,
)


class HomeopathicDashboardView(APIView):
    permission_classes = [IsOrganizationOwner]

    def get(self, request):
        organization = getattr(request, "organization", None)

        if organization is None:
            return Response(
                {"detail": "Organization is required."},
                status=400,
            )

        try:
            months = int(request.query_params.get("months", 6))
        except (TypeError, ValueError):
            months = 6

        # Prevent unnecessarily large dashboard queries
        months = max(1, min(months, 24))

        today = timezone.localdate()

        # ---------------------------------------------------------
        # Base querysets
        # ---------------------------------------------------------

        patients = HomeopathicPatient.objects.filter(organization=organization)

        appointments = HomeopathicAppointment.objects.filter(organization=organization)

        medicines = HomeopathicMedicine.objects.filter(organization=organization)

        prescriptions = HomeopathicPrescription.objects.filter(
            appointment__organization=organization
        )

        # ---------------------------------------------------------
        # Summary
        # ---------------------------------------------------------

        total_patients = patients.count()
        active_patients = patients.filter(status="ACTIVE").count()
        total_appointments = appointments.count()
        today_appointments = appointments.filter(created_at__date=today).count()
        total_medicines = medicines.count()
        available_medicines = medicines.filter(status="AVAILABLE").count()
        total_prescriptions = prescriptions.count()

        # ---------------------------------------------------------
        # Patient growth
        # ---------------------------------------------------------

        patient_growth = (
            patients.annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )

        patient_growth = [
            {
                "month": item["month"].strftime("%b %Y"),
                "count": item["count"],
            }
            for item in patient_growth
        ]

        # ---------------------------------------------------------
        # Appointment growth
        # ---------------------------------------------------------

        appointment_growth = (
            appointments.annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )

        appointment_growth = [
            {
                "month": item["month"].strftime("%b %Y"),
                "count": item["count"],
            }
            for item in appointment_growth
        ]

        # ---------------------------------------------------------
        # Appointment status
        # ---------------------------------------------------------

        appointment_status = (
            appointments.values("status").annotate(count=Count("id")).order_by("-count")
        )

        appointment_status = [
            {
                "status": item["status"],
                "count": item["count"],
            }
            for item in appointment_status
        ]

        # ---------------------------------------------------------
        # Patient status
        # ---------------------------------------------------------

        patient_status = (
            patients.values("status").annotate(count=Count("id")).order_by("-count")
        )

        patient_status = [
            {
                "status": item["status"],
                "count": item["count"],
            }
            for item in patient_status
        ]

        # ---------------------------------------------------------
        # Medicine status
        # ---------------------------------------------------------

        medicine_status = (
            medicines.values("status").annotate(count=Count("id")).order_by("-count")
        )

        medicine_status = [
            {
                "status": item["status"],
                "count": item["count"],
            }
            for item in medicine_status
        ]

        # ---------------------------------------------------------
        # Top prescribed medicines
        # ---------------------------------------------------------

        top_medicines = (
            prescriptions.values(
                "medicine__uid",
                "medicine__name",
            )
            .annotate(prescription_count=Count("id"))
            .order_by("-prescription_count")[:10]
        )

        top_medicines = [
            {
                "medicine_uid": item["medicine__uid"],
                "name": item["medicine__name"],
                "prescription_count": item["prescription_count"],
            }
            for item in top_medicines
        ]

        # ---------------------------------------------------------
        # Response
        # ---------------------------------------------------------

        data = {
            "summary": {
                "total_patients": total_patients,
                "active_patients": active_patients,
                "total_appointments": total_appointments,
                "today_appointments": today_appointments,
                "total_medicines": total_medicines,
                "available_medicines": available_medicines,
                "total_prescriptions": total_prescriptions,
            },
            "patient_growth": patient_growth,
            "appointment_growth": appointment_growth,
            "appointment_status": appointment_status,
            "patient_status": patient_status,
            "medicine_status": medicine_status,
            "top_medicines": top_medicines,
        }

        serializer = HomeopathicDashboardSerializer(data)

        return Response(serializer.data)


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

    filterset_fields = ["homeopathic_patient__miasm_type"]

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
        organization = getattr(
            self.request,
            "organization",
            None,
        )

        return (
            HomeopathicAppointment.objects.filter(
                organization=organization,
            )
            .select_related(
                "homeopathic_patient",
                "homeopathic_patient__user",
            )
            .prefetch_related(
                "appointment_prescription__medicine",
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
        organization = getattr(
            self.request,
            "organization",
            None,
        )

        return (
            HomeopathicAppointment.objects.filter(
                organization=organization,
            )
            .select_related(
                "homeopathic_patient",
                "homeopathic_patient__user",
            )
            .prefetch_related(
                "appointment_prescription__medicine",
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

        queryset = (
            HomeopathicMedicine.objects.filter(
                organization=organization,
            )
            .prefetch_related("attachments")
            .order_by("-created_at")
        )

        appointment_uid = self.request.query_params.get("appointment_uid")

        if appointment_uid:
            queryset = queryset.exclude(
                medicine_prescriptions__appointment__uid=appointment_uid,
                medicine_prescriptions__appointment__organization=organization,
            )

        return queryset


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

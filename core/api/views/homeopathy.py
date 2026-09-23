from collections import defaultdict

from django.db.models import Count, F, Q, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone

from rest_framework import status
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.homeopathy.models import (
    HomeopathicPatient,
    HomeopathicMedicine,
    HomeopathicAppointment,
    HomeopathicPrescription,
)
from apps.homeopathy.choices import HomeopathicAppointmentStatus

from common.permissions import IsOrganizationOwner

from ..serializers.homeopathy import (
    HomeopathicDashboardSerializer,
    HomeopathicPatientSerializer,
    HomeopathicAppointmentSerializer,
    HomeopathicMedicineSerializer,
    RepertorySerializer,
    RepertoryChapterSerializer,
    RepertoryRubricSerializer,
    RepertoryRemedySerializer,
    RepertoryRemedyAnalysisSerializer,
)
from apps.homeopathy.models import (
    Repertory,
    RepertoryChapter,
    RepertoryRubric,
    RepertoryRemedy,
    RemedyRubric,
)


class RepertoryListView(ListAPIView):
    serializer_class = RepertorySerializer

    def get_queryset(self):
        return Repertory.objects.filter(is_active=True).order_by("name")


class RepertoryChapterListView(ListAPIView):
    serializer_class = RepertoryChapterSerializer

    def get_queryset(self):
        return RepertoryChapter.objects.filter(
            repertory__uid=self.kwargs["repertory_uid"],
            repertory__is_active=True,
        ).order_by("source_id")


class RepertoryRubricListView(ListAPIView):
    serializer_class = RepertoryRubricSerializer
    search_fields = [
        "text",
        "full_path",
        "source_abbreviation",
    ]

    def get_queryset(self):
        queryset = RepertoryRubric.objects.filter(
            repertory__uid=self.kwargs["repertory_uid"],
            repertory__is_active=True,
        ).select_related("chapter", "parent")

        chapter_uid = self.request.query_params.get("chapter_uid")
        parent_uid = self.request.query_params.get("parent_uid")

        if chapter_uid:
            queryset = queryset.filter(chapter__uid=chapter_uid)
        if parent_uid:
            queryset = queryset.filter(parent__uid=parent_uid)

        return queryset.order_by("source_id")


class RepertoryAnalysisView(APIView):

    def post(self, request, repertory_uid):
        rubric_uids = request.data.get("rubric_uids", [])

        if not rubric_uids:
            return Response(
                {"detail": "At least one rubric is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        rubric_uids = list(set(rubric_uids))

        selected_rubrics = list(
            RepertoryRubric.objects.filter(
                uid__in=rubric_uids,
                repertory__uid=repertory_uid,
                repertory__is_active=True,
            ).select_related("chapter", "parent")
        )

        if len(selected_rubrics) != len(rubric_uids):
            return Response(
                {"detail": "One or more rubrics are invalid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        rubric_map = {str(rubric.uid): rubric for rubric in selected_rubrics}

        relations = RemedyRubric.objects.filter(
            rubric__uid__in=rubric_uids,
            remedy__repertory__uid=repertory_uid,
            remedy__repertory__is_active=True,
        ).select_related("rubric", "remedy")

        remedy_data = defaultdict(
            lambda: {
                "remedy": None,
                "matched_rubrics": [],
                "total_grade": 0,
            }
        )

        for relation in relations:
            remedy_uid = str(relation.remedy.uid)

            data = remedy_data[remedy_uid]

            data["remedy"] = relation.remedy
            data["total_grade"] += relation.grade

            data["matched_rubrics"].append(
                {
                    "rubric_uid": str(relation.rubric.uid),
                    "rubric": relation.rubric.text,
                    "full_path": relation.rubric.full_path,
                    "grade": relation.grade,
                }
            )

        remedies = []

        total_selected = len(selected_rubrics)

        for data in remedy_data.values():

            matched_count = len(data["matched_rubrics"])

            match_percentage = round(
                (matched_count / total_selected) * 100,
                2,
            )

            remedy = data["remedy"]

            remedies.append(
                {
                    "uid": str(remedy.uid),
                    "abbreviation": remedy.abbreviation,
                    "name": remedy.name,
                    "alternative_name": remedy.alternative_name,
                    "total_selected": total_selected,
                    "matched_count": matched_count,
                    "match_percentage": match_percentage,
                    "total_grade": data["total_grade"],
                    "matched_rubrics": data["matched_rubrics"],
                }
            )

        remedies.sort(
            key=lambda item: (
                -item["matched_count"],
                -item["total_grade"],
                item["name"],
            )
        )

        return Response(
            {
                "total_selected": total_selected,
                "remedies": remedies,
            }
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

        # ---------------------------------------------------------
        # Summary
        # ---------------------------------------------------------

        total_patients = patients.count()
        active_patients = patients.filter(status="ACTIVE").count()
        total_appointments = appointments.count()
        today_appointments = appointments.filter(created_at__date=today).count()
        total_medicines = medicines.count()
        available_medicines = medicines.filter(status="AVAILABLE").count()

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

        # top_medicines = (
        #     prescriptions.values(
        #         "medicine__uid",
        #         "medicine__name",
        #     )
        #     .annotate(prescription_count=Count("id"))
        #     .order_by("-prescription_count")[:10]
        # )

        # top_medicines = [
        #     {
        #         "medicine_uid": item["medicine__uid"],
        #         "name": item["medicine__name"],
        #         "prescription_count": item["prescription_count"],
        #     }
        #     for item in top_medicines
        # ]

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
            },
            "patient_growth": patient_growth,
            "appointment_growth": appointment_growth,
            "patient_status": patient_status,
            "medicine_status": medicine_status,
            # "top_medicines": top_medicines,
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

    filterset_fields = {
        "status": ["exact"],
        "appointment_date": ["gte", "lte"],
    }

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

        queryset = (
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

        # When requesting today's scheduled appointments,
        # order by patient serial number.
        status = self.request.query_params.get("status")
        appointment_date = self.request.query_params.get("appointment_date")

        today = timezone.localdate()

        if (
            status == HomeopathicAppointmentStatus.SCHEDULED
            and appointment_date == str(today)
        ):
            return queryset.order_by(
                "homeopathic_patient__serial_number",
            )

        return queryset.order_by("-created_at")


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

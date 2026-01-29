from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.views import APIView

from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from apps.authentication.choices import UserStatus
from apps.homeopathy.models import (
    HomeopathicPatient,
    HomeopathicAppointment,
    HomeopathicMedicine,
)
from apps.homeopathy.choices import (
    HomeopathicPatientStatus,
    HomeopathicAppointmentStatus,
    HomeopathicMedicineStatus,
)
from apps.organizations.models import Organization, OrganizationMember

from common.filters import HomeopathicMedicineFilter
from common.permissions import IsOrganizationMember

from ..serializers.homeopathy import (
    HomeopathicProfileDetailSerializer,
    HomeopathicPatientListSerializer,
    HomeopathicAppointmentSerializer,
    HomeopathicPatientDetailSerializer,
    HomeopathicPatientAppointmentListSerializer,
    HomeopathicAppointmentDetailSerializer,
    HomeopathicMedicineSerializer,
)


class HomeopathicDashboardView(APIView):
    pass


class HomeopathicProfileDetailView(RetrieveUpdateAPIView):
    queryset = OrganizationMember.objects.all()
    serializer_class = HomeopathicProfileDetailSerializer
    permission_classes = []

    def get_object(self):
        organization_uid = self.kwargs.get("organization_uid")
        return self.queryset.get(organization__uid=organization_uid)


# Homeopathic patient views
class HomeopathicPatientListView(ListCreateAPIView):
    queryset = HomeopathicPatient.objects.all()
    serializer_class = HomeopathicPatientListSerializer
    permission_classes = [IsOrganizationMember]

    def get_queryset(self):
        organization_uid = self.kwargs.get("organization_uid")

        return self.queryset.filter(organization__uid=organization_uid)


class HomeopathicPatientDetailView(RetrieveUpdateDestroyAPIView):
    queryset = HomeopathicPatient.objects.all()
    serializer_class = HomeopathicPatientDetailSerializer
    permission_classes = [IsOrganizationMember]

    def get_object(self):
        organization_uid = self.kwargs.get("organization_uid")
        patient_uid = self.kwargs.get("patient_uid")
        return self.queryset.get(uid=patient_uid, organization__uid=organization_uid)

    def perform_destroy(self, instance):
        instance.user.status = UserStatus.DELETED
        instance.user.save()
        instance.status = HomeopathicPatientStatus.DELETED
        instance.save()


# Homeopathis appointment views
class HomeopathicAppointmentListView(ListCreateAPIView):
    queryset = HomeopathicAppointment.objects.all()
    serializer_class = HomeopathicAppointmentSerializer


class HomeopathicAppointmentDetailView(RetrieveUpdateDestroyAPIView):
    queryset = HomeopathicAppointment.objects.all()
    serializer_class = HomeopathicAppointmentSerializer


# Homeopathic patient appointment views
class HomeopathicPatientppointmentListView(ListCreateAPIView):
    queryset = HomeopathicAppointment.objects.all()
    serializer_class = HomeopathicPatientAppointmentListSerializer
    permission_classes = [IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = {
        "created_at": ["exact", "gt", "lt"],
        "updated_at": ["exact", "gt", "lt"],
    }
    search_fields = [
        "homeopathic_patient__user__first_name",
        "homeopathic_patient__user__last_name",
        "homeopathic_patient__serial_number",
        "homeopathic_patient__old_serial_number",
    ]

    def get_queryset(self):
        recent = self.request.query_params.get("recent")

        organization_uid = self.kwargs.get("organization_uid")
        patient_uid = self.kwargs.get("patient_uid")

        base_queryset = self.queryset.filter(
            organization__uid=organization_uid, homeopathic_patient__uid=patient_uid
        )

        if recent == "true":
            return base_queryset.order_by("-created_at")[:1]

        return base_queryset


class HomeopathicPatientAppointmentDetailView(RetrieveUpdateDestroyAPIView):
    queryset = HomeopathicAppointment.objects.all()
    serializer_class = HomeopathicAppointmentDetailSerializer
    permission_classes = [IsOrganizationMember]

    def get_object(self):
        organization_uid = self.kwargs.get("organization_uid")
        patient_uid = self.kwargs.get("patient_uid")
        appointment_uid = self.kwargs.get("appointment_uid")

        return self.queryset.get(
            organization__uid=organization_uid,
            homeopathic_patient__uid=patient_uid,
            uid=appointment_uid,
        )

    def perform_destroy(self, instance):
        instance.status = HomeopathicAppointmentStatus.DELETED
        instance.save()


# Medicine views
class HomeopathicMedicineListView(ListCreateAPIView):
    queryset = HomeopathicMedicine.objects.all()
    serializer_class = HomeopathicMedicineSerializer
    permission_classes = [IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, SearchFilter]

    search_fields = ["name", "manufacturer"]
    filterset_fields = {
        "is_available": ["exact"],
        "expiration_date": ["exact", "gt", "lt"],
    }
    ordering_fields = ["created_at"]

    def perform_create(self, serializer):
        organization_uid = self.kwargs.get("organization_uid")
        organization = Organization.objects.filter(uid=organization_uid).first()
        serializer.save(organization=organization)

    def get_queryset(self):
        organization_uid = self.kwargs.get("organization_uid")

        return self.queryset.filter(
            organization__uid=organization_uid,
            status=HomeopathicMedicineStatus.AVAILABLE,
        )


class HomeopathicMedicineDetailView(RetrieveUpdateDestroyAPIView):
    queryset = HomeopathicMedicine.objects.all()
    serializer_class = HomeopathicMedicineSerializer
    permission_classes = [IsOrganizationMember]

    def get_object(self):
        organization_uid = self.kwargs.get("organization_uid")
        medicine_uid = self.kwargs.get("medicine_uid")
        return self.queryset.get(
            organization__uid=organization_uid,
            uid=medicine_uid,
            status=HomeopathicMedicineStatus.AVAILABLE,
        )

    def perform_destroy(self, instance):
        instance.status = HomeopathicMedicineStatus.DELETED
        instance.save()

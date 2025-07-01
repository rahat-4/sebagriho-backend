from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,
)

from django_filters.rest_framework import DjangoFilterBackend

from common.filters import HomeopathicMedicineFilter

from apps.authentication.choices import UserStatus
from apps.homeopathy.models import (
    HomeopathicPatient,
    HomeopathicAppointment,
    HomeopathicMedicine,
)
from apps.homeopathy.choices import (
    HomeopathicPatientStatus,
    MiasmType,
    HomeopathicMedicineStatus,
)

from apps.organizations.models import Organization, OrganizationMember

from common.permissions import IsOrganizationMember

from ..serializers.homeopathy import (
    HomeopathicProfileDetailSerializer,
    HomeopathicPatientListSerializer,
    HomeopathicPatientDetailSerializer,
    HomeopathicPatientAppointmentListSerializer,
    HomeopathicAppointmentDetailSerializer,
    HomeopathicMedicineListSerializer,
    HomeopathicMedicineDetailSerializer,
)


class HomeopathicProfileDetailView(RetrieveUpdateAPIView):
    queryset = OrganizationMember.objects.all()
    serializer_class = HomeopathicProfileDetailSerializer
    permission_classes = [IsOrganizationMember]

    def get_object(self):
        organization_uid = self.kwargs.get("organization_uid")
        return self.queryset.get(organization__uid=organization_uid)


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


class HomeopathicPatientppointmentListView(ListCreateAPIView):
    queryset = HomeopathicAppointment.objects.all()
    serializer_class = HomeopathicPatientAppointmentListSerializer
    permission_classes = [IsOrganizationMember]

    def get_queryset(self):
        organization_uid = self.kwargs.get("organization_uid")
        patient_uid = self.kwargs.get("patient_uid")

        return self.queryset.filter(
            organization__uid=organization_uid, homeopathic_patient__uid=patient_uid
        )


class HomeopathicAppointmentDetailView(RetrieveUpdateDestroyAPIView):
    queryset = HomeopathicAppointment.objects.all()
    serializer_class = HomeopathicAppointmentDetailSerializer
    permission_classes = [IsOrganizationMember]

    def get_object(self):
        uid = self.kwargs.get("uid")
        return self.queryset.get(uid=uid)

    def perform_destroy(self, instance):
        pass


class HomeopathicMedicineListView(ListCreateAPIView):
    queryset = HomeopathicMedicine.objects.all()
    serializer_class = HomeopathicMedicineListSerializer
    permission_classes = [IsOrganizationMember]
    filter_backends = [DjangoFilterBackend]
    # filterset_class = HomeopathicMedicineFilter
    filterset_fields = ["name", "is_available", "expiration_date", "manufacturer"]

    def get_queryset(self):
        organization_uid = self.kwargs.get("organization_uid")

        return self.queryset.filter(organization__uid=organization_uid)


class HomeopathicMedicineDetailView(RetrieveUpdateDestroyAPIView):
    queryset = HomeopathicMedicine.objects.all()
    serializer_class = HomeopathicMedicineDetailSerializer
    permission_classes = [IsOrganizationMember]

    def get_object(self):
        organization_uid = self.kwargs.get("organization_uid")
        medicine_uid = self.kwargs.get("medicine_uid")
        return self.queryset.get(organization__uid=organization_uid, uid=medicine_uid)

    def perform_destroy(self, instance):
        instance.status = HomeopathicMedicineStatus.DELETED
        instance.save()

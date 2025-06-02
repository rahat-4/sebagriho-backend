from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,
)

from apps.authentication.choices import UserStatus
from apps.homeopathy.models import (
    HomeopathicPatient,
    HomeopathicAppointment,
    HomeopathicMedicine,
)
from apps.homeopathy.choices import HomeopathicPatientStatus, MiasmType

from apps.organizations.models import Organization, OrganizationMember

from ..serializers.homeopathy import (
    HomeopathicProfileDetailSerializer,
    HomeopathicPatientListSerializer,
    HomeopathicPatientDetailSerializer,
    HomeopathicAppointmentListSerializer,
    HomeopathicAppointmentDetailSerializer,
    HomeopathicMedicineListSerializer,
    HomeopathicMedicineDetailSerializer,
)


class HomeopathicProfileDetailView(RetrieveUpdateAPIView):
    queryset = OrganizationMember.objects.all()
    serializer_class = HomeopathicProfileDetailSerializer
    permission_classes = []

    def get_object(self):
        uid = self.kwargs.get("organization_uid")
        return self.queryset.get(organization__uid=uid)


class HomeopathicPatientListView(ListCreateAPIView):
    queryset = HomeopathicPatient.objects.all()
    serializer_class = HomeopathicPatientListSerializer
    permission_classes = []


class HomeopathicPatientDetailView(RetrieveUpdateDestroyAPIView):
    queryset = HomeopathicPatient.objects.all()
    serializer_class = HomeopathicPatientDetailSerializer
    permission_classes = []

    def get_object(self):
        patient_uid = self.kwargs.get("patient_uid")
        return self.queryset.get(uid=patient_uid)

    def perform_destroy(self, instance):
        instance.user.status = UserStatus.DELETED
        instance.user.save()
        instance.status = HomeopathicPatientStatus.DELETED
        instance.save()


class HomeopathicAppointmentListView(ListCreateAPIView):
    queryset = HomeopathicAppointment.objects.all()
    serializer_class = HomeopathicAppointmentListSerializer
    permission_classes = []


class HomeopathicAppointmentDetailView(RetrieveUpdateDestroyAPIView):
    queryset = HomeopathicAppointment.objects.all()
    serializer_class = HomeopathicAppointmentDetailSerializer
    permission_classes = []

    def get_object(self):
        uid = self.kwargs.get("uid")
        return self.queryset.get(uid=uid)

    def perform_destroy(self, instance):
        pass


class HomeopathicMedicineListView(ListCreateAPIView):
    queryset = HomeopathicMedicine.objects.all()
    serializer_class = HomeopathicMedicineListSerializer
    permission_classes = []


class HomeopathicMedicineDetailView(RetrieveUpdateDestroyAPIView):
    queryset = HomeopathicMedicine.objects.all()
    serializer_class = HomeopathicMedicineDetailSerializer
    permission_classes = []

    def get_object(self):
        uid = self.kwargs.get("uid")
        return self.queryset.get(uid=uid)

    def perform_destroy(self, instance):
        pass

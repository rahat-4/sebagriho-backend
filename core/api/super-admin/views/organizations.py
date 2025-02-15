from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from apps.organizations.models import Organization
from apps.doctors.models import Doctor

from ..serializers.organizations import (
    OrganizationSerializer,
    OrganizationDoctorListSerializer,
)


class OrganizationList(ListCreateAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer


class OrganizationDetail(RetrieveUpdateDestroyAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    def get_object(self):
        organization_uid = self.kwargs["organization_uid"]

        return Organization.objects.get(uid=organization_uid)


class OrganizationDoctorsList(ListCreateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = OrganizationDoctorListSerializer


class OrganizationDoctorsDetail(RetrieveUpdateDestroyAPIView):
    queryset = Doctor.objects.all()

    def get_object(self):
        doctor_uid = self.kwargs["doctor_uid"]

        return Doctor.objects.get(uid=doctor_uid)

from rest_framework.generics import ListCreateAPIView

from apps.doctors.models import Doctor

from ..serializers.doctors import AdminDoctorListCreateSerializer


class AdminDoctorListCreate(ListCreateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = AdminDoctorListCreateSerializer

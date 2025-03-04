from django.urls import path

from ..views.doctors import AdminDoctorListCreate

urlpatterns = [
    path("", AdminDoctorListCreate.as_view(), name="admin.doctor-list-create"),
]

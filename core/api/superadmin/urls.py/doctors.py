from django.urls import path

from ..views.doctors import AdminDoctorList

urlpatterns = [
    path("/doctors", AdminDoctorList.as_view(), name="admin.doctor-list"),
]

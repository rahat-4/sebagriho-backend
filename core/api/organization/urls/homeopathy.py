from django.urls import path

from ..views.homeopathy import (
    HomeopathicPatientListView,
    HomeopathicPatientDetailView,
    HomeopathicAppointmentListView,
    HomeopathicAppointmentDetailView,
    HomeopathicMedicineListView,
    HomeopathicMedicineDetailView,
)

urlpatterns = [
    path(
        "/patients/<str:serial_number>",
        HomeopathicPatientDetailView.as_view(),
        name="homeopathic-patient-detail",
    ),
    path(
        "/patients",
        HomeopathicPatientListView.as_view(),
        name="homeopathic-patient-list",
    ),
]

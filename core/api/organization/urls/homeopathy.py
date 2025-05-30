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
        "/patients/<uuid:patient_uid>",
        HomeopathicPatientDetailView.as_view(),
        name="homeopathic.patient-detail",
    ),
    path(
        "/patients",
        HomeopathicPatientListView.as_view(),
        name="homeopathic.patient-list",
    ),
]

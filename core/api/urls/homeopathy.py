from django.urls import path

from ..views.homeopathy import (
    HomeopathicPatientListCreateView,
    HomeopathicPatientDetailView,
    HomeopathicAppointmentListCreateView,
    HomeopathicAppointmentDetailView,
    HomeopathicMedicineListCreateView,
    HomeopathicMedicineDetailView,
)

urlpatterns = [
    # Patients
    path(
        "/patients",
        HomeopathicPatientListCreateView.as_view(),
        name="homeopathic-patient-list-create",
    ),
    path(
        "/patients/<uuid:patient_uid>",
        HomeopathicPatientDetailView.as_view(),
        name="homeopathic-patient-detail",
    ),
    # Appointments
    path(
        "/appointments",
        HomeopathicAppointmentListCreateView.as_view(),
        name="homeopathic-appointment-list-create",
    ),
    path(
        "/appointments/<uuid:appointment_uid>",
        HomeopathicAppointmentDetailView.as_view(),
        name="homeopathic-appointment-detail",
    ),
    # Medicines
    path(
        "/medicines",
        HomeopathicMedicineListCreateView.as_view(),
        name="homeopathic-medicine-list-create",
    ),
    path(
        "/medicines/<uuid:medicine_uid>",
        HomeopathicMedicineDetailView.as_view(),
        name="homeopathic-medicine-detail",
    ),
]

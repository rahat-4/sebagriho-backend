from django.urls import path

from ..views.homeopathy import (
    HomeopathicProfileDetailView,
    HomeopathicPatientListView,
    HomeopathicPatientDetailView,
    HomeopathicPatientppointmentListView,
    HomeopathicAppointmentDetailView,
    HomeopathicMedicineListView,
    HomeopathicMedicineDetailView,
)

urlpatterns = [
    path(
        "/<uuid:organization_uid>/medicines/<uuid:medicine_uid>",
        HomeopathicMedicineDetailView.as_view(),
        name="homeopathic.medicine-detail",
    ),
    path(
        "/<uuid:organization_uid>/medicines",
        HomeopathicMedicineListView.as_view(),
        name="homeopathic.medicine-list",
    ),
    path(
        "/<uuid:organization_uid>/patients/<uuid:patient_uid>/appointments/<uuid:appointment_uid>",
        HomeopathicAppointmentDetailView.as_view(),
        name="homeopathic.patient-appointment-detail",
    ),
    path(
        "/<uuid:organization_uid>/patients/<uuid:patient_uid>/appointments",
        HomeopathicPatientppointmentListView.as_view(),
        name="homeopathic.patient-appointment-list",
    ),
    path(
        "/<uuid:organization_uid>/patients/<uuid:patient_uid>",
        HomeopathicPatientDetailView.as_view(),
        name="homeopathic.patient-detail",
    ),
    path(
        "/<uuid:organization_uid>/patients",
        HomeopathicPatientListView.as_view(),
        name="homeopathic.patient-list",
    ),
    path(
        "/profile/<uuid:organization_uid>",
        HomeopathicProfileDetailView.as_view(),
        name="homeopathic.profile-detail",
    ),
]

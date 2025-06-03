from django.urls import path

from ..views.homeopathy import (
    HomeopathicProfileDetailView,
    HomeopathicPatientListView,
    HomeopathicPatientDetailView,
    HomeopathicAppointmentListView,
    HomeopathicAppointmentDetailView,
    HomeopathicMedicineListView,
    HomeopathicMedicineDetailView,
)

urlpatterns = [
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

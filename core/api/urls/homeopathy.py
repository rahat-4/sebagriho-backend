from django.urls import path

from ..views.homeopathy import (
    HomeopathicDashboardView,
    HomeopathicPatientListCreateView,
    HomeopathicPatientDetailView,
    HomeopathicAppointmentListCreateView,
    HomeopathicAppointmentDetailView,
    HomeopathicMedicineListCreateView,
    HomeopathicMedicineDetailView,
    RepertoryListView,
    RepertoryChapterListView,
    RepertoryRubricListView,
    RepertoryRubricSearchView,
    RepertoryRubricRemedyListView,
    RepertoryAnalysisView,
)

urlpatterns = [
    # Repertories
    path(
        "/repertories",
        RepertoryListView.as_view(),
        name="repertory-list",
    ),
    path(
        "/repertories/<uuid:repertory_uid>/chapters",
        RepertoryChapterListView.as_view(),
        name="repertory-chapter-list",
    ),
    path(
        "/repertories/<uuid:repertory_uid>/rubrics/search",
        RepertoryRubricSearchView.as_view(),
        name="repertory-rubric-search",
    ),
    path(
        "/repertories/<uuid:repertory_uid>/rubrics",
        RepertoryRubricListView.as_view(),
        name="repertory-rubric-list",
    ),
    path(
        "/repertories/<uuid:repertory_uid>/analysis",
        RepertoryAnalysisView.as_view(),
        name="repertory-analysis",
    ),
    path(
        "/dashboard", HomeopathicDashboardView.as_view(), name="homeopathic-dashboard"
    ),
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

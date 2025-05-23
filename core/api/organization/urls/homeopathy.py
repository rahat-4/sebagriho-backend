from django.urls import path

from ..views.homeopathy import HomeopathyPatientListView, HomeopathyPatientDetailView

urlpatterns = [
    path(
        "/patients/<str:serial_number>",
        HomeopathyPatientDetailView.as_view(),
        name="homeopathy-patient-detail",
    ),
    path(
        "/patients", HomeopathyPatientListView.as_view(), name="homeopathy-patient-list"
    ),
]

from django.urls import path

from ..views.homeopathy import HomeopathyPatientListView

urlpatterns = [
    path(
        "/patients", HomeopathyPatientListView.as_view(), name="homeopathy-patient-list"
    ),
]

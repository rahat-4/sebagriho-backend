from django.urls import path

from ..views.filters import (
    HomeopathicPatientFilterView,
    HomeopathicMedicineFilterView,
)

urlpatterns = [
    path(
        "/homeopathic-patients",
        HomeopathicPatientFilterView.as_view(),
        name="homeopathic-patient-filter",
    ),
    path(
        "/homeopathic-medicines",
        HomeopathicMedicineFilterView.as_view(),
        name="homeopathic-medicine-filter",
    ),
]

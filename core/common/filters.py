from django_filters.rest_framework import FilterSet, CharFilter

from apps.homeopathy.models import HomeopathicMedicine


class HomeopathicMedicineFilter(FilterSet):
    search = CharFilter(method="filter_by_name")

    def filter_by_name(self, queryset, name, value):
        return queryset.filter(name__icontains=value)

    class Meta:
        model = HomeopathicMedicine
        fields = ["search"]

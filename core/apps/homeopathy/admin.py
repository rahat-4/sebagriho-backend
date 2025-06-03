from django.contrib import admin

from .models import HomeopathicPatient, HomeopathicAppointment, HomeopathicMedicine


admin.site.register(HomeopathicPatient)


@admin.register(HomeopathicAppointment)
class HomeopathicAppointmentAdmin(admin.ModelAdmin):
    list_display = ("uid", "homeopathic_patient", "created_at")
    search_fields = ("homeopathic_patient__name", "created_at")
    list_per_page = 20
    ordering = ("-created_at",)
    fieldsets = (
        (None, {"fields": ("homeopathic_patient", "created_at")}),
        ("Additional Information", {"fields": ("notes",)}),
    )


@admin.register(HomeopathicMedicine)
class HomeopathicMedicineAdmin(admin.ModelAdmin):
    list_display = ("name", "power", "manufacturer")
    search_fields = ("name", "power", "manufacturer")
    list_filter = ("power",)
    list_per_page = 20
    ordering = ("name",)
    fieldsets = (
        (None, {"fields": ("name", "power", "manufacturer")}),
        ("Additional Information", {"fields": ("description",)}),
    )

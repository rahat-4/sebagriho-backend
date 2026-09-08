from django.contrib import admin

from .models import (
    Organization,
    OrganizationMember,
    OrganizationRole,
    PlatformStaff,
)

admin.site.register(PlatformStaff)
admin.site.register(OrganizationMember)
admin.site.register(OrganizationRole)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent", "organization_type", "created_at")
    search_fields = ("name", "slug")
    list_filter = ("parent",)
    ordering = ("-created_at",)

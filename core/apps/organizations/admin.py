from django.contrib import admin

from .models import (
    Organization,
    OrganizationMember,
    OrganizationRole,
)

admin.site.register(Organization)
admin.site.register(OrganizationMember)
admin.site.register(OrganizationRole)

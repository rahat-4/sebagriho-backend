from django.contrib import admin

from .models import Attachment


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("id", "file", "content_type", "object_id", "created_at")
    search_fields = ("file",)
    list_filter = ("content_type", "created_at")

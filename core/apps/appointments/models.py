from django.db import models

from common.models import BaseModelWithUid
from common.utils import unique_number_generator

from .choices import AppointmentType, AppointmentFor, AppointmentStatus
from .utils import get_appointment_slug

class Appointment(BaseModelWithUid):
    slug = models.SlugField(max_length=255, unique=True, blank=True, populate_from=get_appointment_slug)
    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )
    serial_number = models.PositiveIntegerField(unique=True, editable=False)
    appointment_type = models.CharField(max_length=50, choices=AppointmentType.choices, default=AppointmentType.CONSULTATION)
    appointment_for = models.CharField(max_length=50, choices=AppointmentFor.choices, default=AppointmentFor.ME)
    status = models.CharField(max_length=50, choices=AppointmentStatus.choices, blank=True)
    complication = models.CharField(max_length=500, blank=True, null=True)
    is_visible = models.BooleanField(default=False, help_text="Use for visibility.")
    is_previous = models.BooleanField(default=True, help_text="Show previous medical records.")
    cancellation_reason = models.TextField(blank=True, null=True)
    conference_link = models.URLField(blank=True, null=True)
    creator_user = models.ForeignKey("core.user", on_delete=models.CASCADE, help_text="User who created the appointment.", related_name="created_appointments")
    organization = models.ForeignKey("organizations.organization", on_delete=models.CASCADE, related_name="appointments")
    schedule_start = models.DateTimeField(help_text="Start time of the appointment.", blank=True, null=True)
    schedule_end = models.DateTimeField(help_text="End time of the appointment.", blank=True, null=True)

    def __str__(self):
        return f"{self.organization.name} - {self.serial_number}"
    
    def save(self, *args, **kwargs):
        self.serial_number = unique_number_generator(self)
        super().save(*args, **kwargs)


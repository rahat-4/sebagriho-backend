from django.db import models
from django.contrib.auth import get_user_model

from autoslug import AutoSlugField

from common.models import BaseModelWithUid
from common.utils import unique_number_generator

from apps.organizations.models import Organization
from apps.doctors.models import Doctor
from apps.patients.models import Patient, RelativePatient

from .choices import AppointmentType, AppointmentFor, AppointmentStatus
from .utils import get_appointment_slug

User = get_user_model()


class Appointment(BaseModelWithUid):
    slug = AutoSlugField(unique=True, populate_from=get_appointment_slug)
    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )
    serial_number = models.PositiveIntegerField(unique=True, editable=False)
    appointment_type = models.CharField(
        max_length=50,
        choices=AppointmentType.choices,
        default=AppointmentType.CONSULTATION,
    )
    appointment_for = models.CharField(
        max_length=50, choices=AppointmentFor.choices, default=AppointmentFor.ME
    )
    status = models.CharField(
        max_length=50, choices=AppointmentStatus.choices, blank=True
    )
    complication = models.CharField(max_length=500, blank=True, null=True)
    is_visible = models.BooleanField(default=False, help_text="Use for visibility.")
    is_previous = models.BooleanField(
        default=True, help_text="Show previous medical records."
    )
    cancellation_reason = models.TextField(blank=True, null=True)
    conference_link = models.URLField(blank=True, null=True)
    creator_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="User who created the appointment.",
        related_name="created_appointments",
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="patient_appointments",
    )
    relative_patient = models.ForeignKey(
        RelativePatient,
        on_delete=models.CASCADE,
        related_name="relative_patient_appointments",
        blank=True,
        null=True,
    )
    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="doctor_appointments"
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    schedule_start = models.DateTimeField(
        help_text="Start time of the appointment.", blank=True, null=True
    )
    schedule_end = models.DateTimeField(
        help_text="End time of the appointment.", blank=True, null=True
    )

    def __str__(self):
        return f"{self.organization.name} - {self.serial_number}"

    def save(self, *args, **kwargs):
        self.serial_number = unique_number_generator(self)
        super().save(*args, **kwargs)

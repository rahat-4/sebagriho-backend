from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation

from autoslug import AutoSlugField
from phonenumber_field.modelfields import PhoneNumberField

from apps.organizations.models import Organization

from common.models import BaseModelWithUid, Attachment

from .choices import (
    HomeopathicPatientStatus,
    MiasmType,
    HomeopathicAppointmentStatus,
    HomeopathicMedicineStatus,
    HomeopathicPrescriptionMealTiming,
)
from .utils import (
    get_homeopathic_patient_slug,
    get_homeopathic_appointment_slug,
    get_medicine_media_path_prefix,
)

User = get_user_model()


class HomeopathicPatient(BaseModelWithUid):
    serial_number = models.PositiveIntegerField(editable=False)
    slug = AutoSlugField(unique=True, populate_from=get_homeopathic_patient_slug)
    status = models.CharField(
        max_length=20,
        choices=HomeopathicPatientStatus.choices,
        default=HomeopathicPatientStatus.ACTIVE,
    )
    old_serial_number = models.PositiveIntegerField(blank=True, null=True)
    relative_phone = PhoneNumberField(blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    miasm_type = models.CharField(
        max_length=20, choices=MiasmType.choices, blank=True, null=True
    )
    case_history = models.TextField(blank=True, null=True)
    habits = models.TextField(blank=True, null=True)
    attachments = GenericRelation(
        Attachment,
        related_query_name="homeopathic_patient_attachments",
    )

    # FK
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="homeopathic_patients"
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="organization_homeopathic_patients",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "serial_number"],
                name="unique_patient_serial_per_organization",
            ),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.uid}"


class HomeopathicAppointment(BaseModelWithUid):
    slug = AutoSlugField(
        unique=True,
        populate_from=get_homeopathic_appointment_slug,
    )
    symptoms = models.TextField(blank=True, null=True)
    treatment_effectiveness = models.TextField(
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=20,
        choices=HomeopathicAppointmentStatus.choices,
        default=HomeopathicAppointmentStatus.ACTIVE,
    )
    attachments = GenericRelation(
        Attachment,
        related_query_name="homeopathic_appointment_attachments",
    )
    homeopathic_patient = models.ForeignKey(
        HomeopathicPatient,
        on_delete=models.CASCADE,
        related_name="homeopathic_patient_appointments",
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="homeopathic_appointments",
    )

    def __str__(self):
        return (
            f"{self.organization.name} - " f"{self.homeopathic_patient.serial_number}"
        )


class HomeopathicMedicine(BaseModelWithUid):
    avatar = models.ImageField(
        upload_to=get_medicine_media_path_prefix,
        blank=True,
        null=True,
        help_text="Image of the medicine",
    )
    name = models.CharField(max_length=100)
    power = models.PositiveIntegerField(blank=True, null=True)
    expiration_date = models.DateField(blank=True, null=True)
    manufacturer = models.CharField(max_length=255, null=True, blank=True)
    total_quantity = models.PositiveIntegerField(null=True, blank=True)
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    description = models.TextField(null=True, blank=True)
    batch_number = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=HomeopathicMedicineStatus.choices,
        default=HomeopathicMedicineStatus.AVAILABLE,
    )
    attachments = GenericRelation(
        Attachment,
        related_query_name="homeopathic_medicine_attachments",
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="organizations_homeopathic_patients_medicines",
    )

    def __str__(self):
        return f"{self.organization.name}"


class HomeopathicPrescription(BaseModelWithUid):
    appointment = models.ForeignKey(
        HomeopathicAppointment,
        on_delete=models.CASCADE,
        related_name="appointment_prescription",
    )
    medicine = models.ForeignKey(
        HomeopathicMedicine,
        on_delete=models.PROTECT,
        related_name="medicine_prescriptions",
    )
    dosage = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="e.g. 3 pills, 5 drops",
    )
    frequency = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="e.g. 3 times daily, once daily",
    )
    duration = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Duration in days",
    )
    meal_timing = models.CharField(
        max_length=20,
        choices=HomeopathicPrescriptionMealTiming.choices,
        blank=True,
        null=True,
    )
    instructions = models.TextField(
        blank=True,
        null=True,
        help_text="Additional instructions",
    )

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["appointment", "medicine"],
                name="unique_medicine_per_appointment",
            ),
        ]

    def __str__(self):
        return f"{self.medicine.name} - {self.appointment}"

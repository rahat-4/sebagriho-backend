from django.db import models
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import pre_save

from autoslug import AutoSlugField
from phonenumber_field.modelfields import PhoneNumberField

from apps.organizations.models import Organization

from common.models import BaseModelWithUid
from common.utils import unique_number_generator

from .choices import HomeopathicPatientStatus, MiasmType
from .utils import get_homeopathic_patient_slug, get_homeopathic_appointment_slug


User = get_user_model()


class HomeopathicPatient(BaseModelWithUid):
    serial_number = models.PositiveIntegerField(unique=True, editable=False)
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

    # FK
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="homeopathic_patients"
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="organization_homeopathic_patients",
    )

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.uid}"


class HomeopathicAppointment(BaseModelWithUid):
    slug = AutoSlugField(unique=True, populate_from=get_homeopathic_appointment_slug)
    symptoms = models.TextField(blank=True, null=True)
    treatment_effectiveness = models.TextField(blank=True, null=True)
    homeopathic_patient = models.ForeignKey(
        HomeopathicPatient,
        on_delete=models.CASCADE,
        related_name="homeopathic_patient_appointments",
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="organizations_homeopathic_patients_appointments",
    )

    def __str__(self):
        return f"{self.organization.name} - {self.homeopathic_patient.serial_number}"


class HomeopathicMedicine(BaseModelWithUid):
    name = models.CharField(max_length=100)
    power = models.CharField(max_length=100, blank=True, null=True)
    expiration_date = models.DateField(blank=True, null=True)
    is_available = models.BooleanField(default=False)
    manufacturer = models.CharField(max_length=255, null=True, blank=True)
    total_quantity = models.IntegerField(null=True, blank=True)
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    description = models.TextField(null=True, blank=True)
    batch_number = models.CharField(max_length=100, null=True, blank=True)
    homeopathic_patient = models.ForeignKey(
        HomeopathicPatient,
        on_delete=models.SET_NULL,
        related_name="homeopathic_patient_medicines",
        blank=True,
        null=True,
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="organizations_homeopathic_patients_medicines",
    )

    def __str__(self):
        return f"{self.organization.name} - {self.homeopathic_patient.serial_number}"


@receiver(pre_save, sender=HomeopathicPatient)
def set_patient_serial_number(sender, instance, **kwargs):
    if not instance.serial_number:
        instance.serial_number = unique_number_generator(instance)

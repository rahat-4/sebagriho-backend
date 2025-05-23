from django.db import models
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import pre_save

from autoslug import AutoSlugField

from phonenumber_field.modelfields import PhoneNumberField


from apps.authentication.choices import BloodGroups

from common.models import BaseModelWithUid
from common.utils import unique_number_generator

from .choices import PatientStatus, MiasmType
from .utils import get_patient_slug

User = get_user_model()


class Patient(BaseModelWithUid):
    serial_number = models.PositiveIntegerField(unique=True, editable=False)
    slug = AutoSlugField(unique=True, populate_from=get_patient_slug)
    status = models.CharField(
        max_length=20, choices=PatientStatus.choices, default=PatientStatus.ACTIVE
    )
    # Homeopathic
    old_serial_number = models.PositiveIntegerField(blank=True, null=True)
    relative_phone = PhoneNumberField(blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    miasm_type = models.CharField(
        max_length=20, choices=MiasmType.choices, blank=True, null=True
    )
    case_history = models.TextField(blank=True, null=True)
    habits = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="patients")

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.serial_number}"


class RelativePatient(BaseModelWithUid):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="relative_patients"
    )
    patient_relation = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    height = models.FloatField(blank=True, null=True)
    weight = models.PositiveIntegerField(blank=True, null=True)
    blood_group = models.CharField(
        max_length=20, choices=BloodGroups.choices, blank=True, null=True
    )

    def __str__(self):
        return f"{self.patient.user.get_full_name()} - {self.name}"


# Ensure serial number is generated before saving the patient
@receiver(pre_save, sender=Patient)
def set_patient_serial_number(sender, instance, **kwargs):
    if not instance.serial_number:
        instance.serial_number = unique_number_generator(instance)

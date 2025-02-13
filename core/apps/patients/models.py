from django.db import models

from authentication.choices import BloodGroups

from common.models import BaseModelWithUid
from common.utils import unique_number_generator

from .choices import PatientStatus

class Patient(BaseModelWithUid):
    serial_number = models.PositiveIntegerField(unique=True, editable=False)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=PatientStatus.choices, default=PatientStatus.ACTIVE)
    user = models.ForeignKey("authentication.User", on_delete=models.CASCADE, related_name="patients")

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.serial_number}"
    

    def save(self, *args, **kwargs):
        self.serial_number = unique_number_generator(self)
        super().save(*args, **kwargs)

class RelativePatient(BaseModelWithUid):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="relative_patients")
    patient_relation = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    height = models.FloatField(blank=True, null=True)
    weight = models.PositiveIntegerField(blank=True, null=True)
    blood_group = models.CharField(max_length=20, choices=BloodGroups.choices, blank=True, null=True)

    def __str__(self):
        return f"{self.patient.user.get_full_name()} - {self.name}"
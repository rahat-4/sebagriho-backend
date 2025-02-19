from django.db import models

from common.models import BaseModelWithUid
from apps.appointments.models import Appointment
from apps.doctors.models import Doctor
from apps.patients.models import Patient


class Prescription(BaseModelWithUid):
    appointment = models.OneToOneField(
        Appointment, on_delete=models.CASCADE, related_name="prescription"
    )
    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="doctor_prescriptions"
    )
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="patient_prescriptions"
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    duration = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Prescription for {self.patient.user.get_full_name()} by Dr. {self.doctor.user.get_full_name()}"


class PrescriptionItem(BaseModelWithUid):
    prescription = models.ForeignKey(
        Prescription, on_delete=models.CASCADE, related_name="items"
    )
    medicine_name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=100)
    instructions = models.TextField(blank=True, null=True)
    quantity = models.IntegerField()
    frequency = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.medicine_name} - {self.dosage}"

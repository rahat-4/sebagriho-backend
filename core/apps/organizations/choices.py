from django.db import models

class OrganizationType(models.TextChoices):
    CHAMBER = "CHAMBER", "Chamber"
    HOSPITAL = "HOSPITAL", "Hospital"
    CLINIC = "CLINIC", "Clinic"
    LABORATORY = "LABORATORY", "Laboratory"
    PHARMACY = "PHARMACY", "Pharmacy"
    DIAGNOSTIC_CENTER = "DIAGNOSTIC_CENTER", "Diagnostic Center"
    BLOOD_BANK = "BLOOD_BANK", "Blood Bank"
    AMBULANCE_SERVICE = "AMBULANCE_SERVICE", "Ambulance Service"


class OrganizationStatus(models.TextChoices):
    OPEN = "OPEN", "Open"
    CLOSED = "CLOSED", "CLOSED"

class OrganizationUserRole(models.TextChoices):
    OWNER = "OWNER", "Owner"
    ADMIN = "ADMIN", "Admin"
    MANAGER = "MANAGER", "Manager"
    STAFF = "STAFF", "Staff"
    DOCTOR = "DOCTOR", "Doctor"
    NURSE = "NURSE", "Nurse"
    PHARMACIST = "PHARMACIST", "Pharmacist"
    LAB_TECHNICIAN = "LAB_TECHNICIAN", "Lab Technician"
    RECEPTIONIST = "RECEPTIONIST", "Receptionist"
    AMBULANCE_DRIVER = "AMBULANCE_DRIVER", "Ambulance Driver"
    PATIENT = "PATIENT", "Patient"
    VISITOR = "VISITOR", "Visitor"
    OTHER = "OTHER", "Other"
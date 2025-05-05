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
    HOMEOPATHIC = "HOMEO_PATHIC", "Homeopathic"
    AYURVEDIC = "AYURVEDIC", "Ayurvedic"
    DENTAL = "DENTAL", "Dental"
    VETERINARY = "VETERINARY", "Veterinary"


class OrganizationStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    PENDING = "PENDING", "Pending"
    INACTIVE = "INACTIVE", "Inactive"
    DELETED = "DELETED", "Deleted"
    SUSPENDED = "SUSPENDED", "Suspended"

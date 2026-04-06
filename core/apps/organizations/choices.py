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
    HOMEOPATHY = "HOMEOPATHY", "Homeopathy"
    AYURVEDIC = "AYURVEDIC", "Ayurvedic"
    DENTAL = "DENTAL", "Dental"
    VETERINARY = "VETERINARY", "Veterinary"


class OrganizationStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    PENDING = "PENDING", "Pending"
    INACTIVE = "INACTIVE", "Inactive"
    DELETED = "DELETED", "Deleted"
    SUSPENDED = "SUSPENDED", "Suspended"


class OrganizationMemberStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    INACTIVE = "INACTIVE", "Inactive"
    SUSPENDED = "SUSPENDED", "Suspended"


class AppearanceFontFamilyType(models.TextChoices):
    ROBOTO = "ROBOTO", "Roboto"
    POPPINS = "POPPINS", "Poppins"
    PLAYFAIR_DISPLAY = "PLAYFAIR_DISPLAY", "Playfair Display"
    RALEWAY = "RALEWAY", "Raleway"
    SATISFY = "SATISFY", "Satisfy"
    KARLA = "KARLA", "Karla"
    MONTSERRAT = "MONTSERRAT", "Montserrat"
    INTER = "INTER", "Inter"
    CAVEAT = "CAVEAT", "Caveat"
    OPEN_SANS = "OPEN_SANS", "Open Sans"

from django.db import models


class HomeopathicPatientStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    INACTIVE = "INACTIVE", "Inactive"
    REMOVED = "REMOVED", "Removed"
    DELETED = "DELETED", "Deleted"


class MiasmType(models.TextChoices):
    ACUTE = "ACUTE", "Acute"
    TYPHOID = "TYPHOID", "Typhoid"
    MALARIAL = "MALARIAL", "Malarial"
    RINGWORM = "RINGWORM", "Ringworm"
    PSORIC = "PSORIC", "Psoric"
    SYCOTIC = "SYCOTIC", "Sycotic"
    CANCER = "CANCER", "Cancer"
    TUBERCULAR = "TUBERCULAR", "Tubercular"
    LEPROSY = "LEPROSY", "Leprosy"
    SYPHILITIC = "SYPHILITIC", "Syphilitic"
    AIDS = "AIDS", "AIDS"

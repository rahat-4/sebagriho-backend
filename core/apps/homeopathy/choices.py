from django.db import models
from django.utils.translation import gettext_lazy as _


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


class HomeopathicAppointmentStatus(models.TextChoices):
    SCHEDULED = "SCHEDULED", "Scheduled"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"
    ABSENT = "ABSENT", "Absent"


class HomeopathicMedicineStatus(models.TextChoices):
    AVAILABLE = "AVAILABLE", "Available"
    UNAVAILABLE = "UNAVAILABLE", "Unavailable"


class HomeopathicPrescriptionMealTiming(models.TextChoices):
    BEFORE_MEAL = "BEFORE_MEAL", _("Before Meal")
    AFTER_MEAL = "AFTER_MEAL", _("After Meal")
    WITH_MEAL = "WITH_MEAL", _("With Meal")
    BETWEEN_MEALS = "BETWEEN_MEALS", _("Between Meals")
    BEDTIME = "BEDTIME", _("At Bedtime")
    EMPTY_STOMACH = "EMPTY_STOMACH", _("On Empty Stomach")
    ANY_TIME = "ANY_TIME", _("Any Time")

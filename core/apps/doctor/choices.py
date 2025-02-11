from django.db import models


class DepartmentType(models.TextChoices):
    MEDICAL = "MEDICAL", "Medical"
    DENTAL = "DENTAL", "Dental"

class AffiliationStatus(models.TextChoices):
    CURRENT = "CURRENT", "Current"
    PAST = "PAST", "Past"


class DoctorStatus(models.TextChoices):
    INVITED = "INVITED", "Invited"
    PENDING = "PENDING", "Pending"
    ACTIVE = "ACTIVE", "Active"
    REJECTED = "REJECTED", "Rejected"
    REMOVED = "REMOVED", "Removed"


class ScheduleStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    REMOVED = "REMOVED", "Removed"


class ShiftStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    MORNING = "MORNING", "Morning"
    EVENING = "EVENING", "Evening"


class DayStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    SATURDAY = "SATURDAY", "Saturday"
    SUNDAY = "SUNDAY", "Sunday"
    MONDAY = "MONDAY", "Monday"
    TUESDAY = "TUESDAY", "Tuesday"
    WEDNESDAY = "WEDNESDAY", "Wednesday"
    THURSDAY = "THURSDAY", "Thursday"
    FRIDAY = "FRIDAY", "Friday"

from django.db import models

class AppointmentType(models.TextChoices):
    CONSULTATION = "CONSULTATION", "Consultation"
    FOLLOWUP = "FOLLOWUP", "Followup"


class AppointmentFor(models.TextChoices):
    ME = "ME", "Me"
    RELATIVES = "RELATIVES", "Relatives"
    SOMEONE_ELSE = "SOMEONE_ELSE", "Someone else"

class AppointmentStatus(models.TextChoices):
    REQUESTED = "REQUESTED", "Requested"
    SCHEDULED = "SCHEDULED", "Scheduled"
    PENDING = "PENDING", "Pending"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"
    REMOVED = "REMOVED", "Removed"
    HIDDEN = "HIDDEN", "Hidden"
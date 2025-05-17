from django.db import models


class DosageForm(models.TextChoices):
    TABLET = "Tablet", "Tablet"
    CAPSULE = "Capsule", "Capsule"
    SYRUP = "Syrup", "Syrup"
    INJECTION = "Injection", "Injection"
    OINTMENT = "Ointment", "Ointment"
    DROPS = "Drops", "Drops"
    POWDER = "Powder", "Powder"
    CREAM = "Cream", "Cream"
    GEL = "Gel", "Gel"

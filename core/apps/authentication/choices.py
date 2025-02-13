from django.db import models


class UserStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    ACTIVE = "ACTIVE", "Active"
    PAUSED = "PAUSED", "Paused"
    REMOVED = "REMOVED", "Removed"


class UserGender(models.TextChoices):
    FEMALE = "FEMALE", "Female"
    MALE = "MALE", "Male"
    OTHER = "OTHER", "Other"


class BloodGroups(models.TextChoices):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"

class MethodType(models.TextChoices):
    GET = "GET", "Read"
    POST = "POST", "Create"
    DETAIL = "DETAIL", "View Detail"
    PUT = "PUT", "Update"
    DELETE = "DELETE", "Delete"
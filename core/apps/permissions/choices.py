from django.db import models


class MethodType(models.TextChoices):
    GET = "GET", "Read"
    POST = "POST", "Create"
    DETAIL = "DETAIL", "View Detail"
    PUT = "PUT", "Update"
    DELETE = "DELETE", "Delete"

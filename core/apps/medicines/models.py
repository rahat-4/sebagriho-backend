from django.db import models

from common.models import BaseModelWithUid

from .choices import DosageForm


class Medicine(BaseModelWithUid):
    name = models.CharField(max_length=255)
    generic_name = models.CharField(max_length=255, null=True, blank=True)
    power = models.CharField(max_length=255, null=True, blank=True)
    dosage_form = models.CharField(
        max_length=50, choices=DosageForm.choices, null=True, blank=True
    )
    expiration_date = models.DateField(null=True, blank=True)
    manufacturer = models.CharField(max_length=255, null=True, blank=True)
    total_quantity = models.IntegerField(null=True, blank=True)
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    description = models.TextField(null=True, blank=True)
    batch_number = models.CharField(max_length=100, null=True, blank=True)
    is_prescription_required = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

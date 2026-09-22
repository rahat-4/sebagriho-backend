from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation

from autoslug import AutoSlugField
from phonenumber_field.modelfields import PhoneNumberField

from apps.organizations.models import Organization

from common.models import BaseModelWithUid, Attachment

from .choices import (
    HomeopathicPatientStatus,
    MiasmType,
    HomeopathicAppointmentStatus,
    HomeopathicMedicineStatus,
    HomeopathicPrescriptionMealTiming,
)
from .utils import (
    get_homeopathic_patient_slug,
    get_homeopathic_appointment_slug,
    get_medicine_media_path_prefix,
)

User = get_user_model()


class HomeopathicPatient(BaseModelWithUid):
    serial_number = models.PositiveIntegerField(editable=False)
    slug = AutoSlugField(unique=True, populate_from=get_homeopathic_patient_slug)
    status = models.CharField(
        max_length=20,
        choices=HomeopathicPatientStatus.choices,
        default=HomeopathicPatientStatus.ACTIVE,
    )
    old_serial_number = models.PositiveIntegerField(blank=True, null=True)
    relative_phone = PhoneNumberField(blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    miasm_type = models.CharField(
        max_length=20, choices=MiasmType.choices, blank=True, null=True
    )
    case_history = models.TextField(blank=True, null=True)
    habits = models.TextField(blank=True, null=True)
    attachments = GenericRelation(
        Attachment,
        related_query_name="homeopathic_patient_attachments",
    )

    # FK
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="homeopathic_patients"
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="organization_homeopathic_patients",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "serial_number"],
                name="unique_patient_serial_per_organization",
            ),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.uid}"


class HomeopathicAppointment(BaseModelWithUid):
    slug = AutoSlugField(
        unique=True,
        populate_from=get_homeopathic_appointment_slug,
    )
    serial_number = models.PositiveIntegerField(editable=False)
    appointment_date = models.DateField(default=timezone.now)
    symptoms = models.TextField(blank=True, null=True)
    treatment_effectiveness = models.TextField(
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=20,
        choices=HomeopathicAppointmentStatus.choices,
        default=HomeopathicAppointmentStatus.SCHEDULED,
    )
    attachments = GenericRelation(
        Attachment,
        related_query_name="homeopathic_appointment_attachments",
    )
    homeopathic_patient = models.ForeignKey(
        HomeopathicPatient,
        on_delete=models.CASCADE,
        related_name="homeopathic_patient_appointments",
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="homeopathic_appointments",
    )

    class Meta:
        ordering = ["appointment_date", "serial_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "appointment_date", "serial_number"],
                name="unique_appointment_serial_per_org_per_day",
            ),
        ]

    def __str__(self):
        return f"{self.organization.name} - Serial #{self.serial_number} ({self.appointment_date})"


class HomeopathicMedicine(BaseModelWithUid):
    avatar = models.ImageField(
        upload_to=get_medicine_media_path_prefix,
        blank=True,
        null=True,
        help_text="Image of the medicine",
    )
    name = models.CharField(max_length=100)
    power = models.PositiveIntegerField(blank=True, null=True)
    expiration_date = models.DateField(blank=True, null=True)
    manufacturer = models.CharField(max_length=255, null=True, blank=True)
    total_quantity = models.PositiveIntegerField(null=True, blank=True)
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    description = models.TextField(null=True, blank=True)
    batch_number = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=HomeopathicMedicineStatus.choices,
        default=HomeopathicMedicineStatus.AVAILABLE,
    )
    attachments = GenericRelation(
        Attachment,
        related_query_name="homeopathic_medicine_attachments",
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="organizations_homeopathic_patients_medicines",
    )

    def __str__(self):
        return f"{self.organization.name}"


class HomeopathicPrescription(BaseModelWithUid):
    appointment = models.ForeignKey(
        HomeopathicAppointment,
        on_delete=models.CASCADE,
        related_name="appointment_prescription",
    )
    medicine = models.ForeignKey(
        HomeopathicMedicine,
        on_delete=models.PROTECT,
        related_name="medicine_prescriptions",
    )
    dosage = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="e.g. 3 pills, 5 drops",
    )
    frequency = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="e.g. 3 times daily, once daily",
    )
    duration = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Duration in days",
    )
    meal_timing = models.CharField(
        max_length=20,
        choices=HomeopathicPrescriptionMealTiming.choices,
        blank=True,
        null=True,
    )
    instructions = models.TextField(
        blank=True,
        null=True,
        help_text="Additional instructions",
    )

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["appointment", "medicine"],
                name="unique_medicine_per_appointment",
            ),
        ]

    def __str__(self):
        return f"{self.medicine.name} - {self.appointment}"


class Repertory(BaseModelWithUid):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    source = models.CharField(max_length=255, blank=True)
    version = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class RepertoryChapter(BaseModelWithUid):
    repertory = models.ForeignKey(
        Repertory,
        on_delete=models.CASCADE,
        related_name="chapters",
    )
    source_id = models.IntegerField()
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["repertory", "source_id"],
                name="unique_repertory_chapter_source",
            )
        ]


class RepertoryRubric(BaseModelWithUid):
    repertory = models.ForeignKey(
        Repertory,
        on_delete=models.CASCADE,
        related_name="rubrics",
    )
    source_id = models.IntegerField()
    chapter = models.ForeignKey(
        RepertoryChapter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rubrics",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )
    text = models.CharField(max_length=500)
    full_path = models.TextField()
    source_abbreviation = models.CharField(
        max_length=270,
        default="publicum",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["repertory", "source_id"],
                name="unique_repertory_rubric_source",
            )
        ]
        indexes = [
            models.Index(fields=["repertory", "source_id"]),
            models.Index(fields=["parent"]),
        ]


class RubricTranslation(BaseModelWithUid):
    rubric = models.ForeignKey(
        RepertoryRubric,
        on_delete=models.CASCADE,
        related_name="translations",
    )
    language = models.CharField(
        max_length=10,
        default="bn",
    )
    text = models.TextField()
    full_path = models.TextField()
    is_verified = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["rubric", "language"],
                name="unique_rubric_translation_language",
            )
        ]


class RepertoryRemedy(BaseModelWithUid):
    repertory = models.ForeignKey(
        Repertory,
        on_delete=models.CASCADE,
        related_name="remedies",
    )
    source_id = models.IntegerField()
    abbreviation = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    alternative_name = models.CharField(
        max_length=255,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["repertory", "source_id"],
                name="unique_repertory_remedy_source",
            )
        ]


class RemedyRubric(BaseModelWithUid):
    rubric = models.ForeignKey(
        RepertoryRubric,
        on_delete=models.CASCADE,
        related_name="remedy_relations",
    )
    remedy = models.ForeignKey(
        RepertoryRemedy,
        on_delete=models.CASCADE,
        related_name="rubric_relations",
    )
    grade = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["rubric", "remedy"],
                name="unique_remedy_rubric",
            )
        ]
        indexes = [
            models.Index(fields=["rubric"]),
            models.Index(fields=["remedy"]),
            models.Index(fields=["rubric", "grade"]),
        ]


class AppointmentRubric(BaseModelWithUid):
    appointment = models.ForeignKey(
        HomeopathicAppointment,
        on_delete=models.CASCADE,
        related_name="selected_rubrics",
    )
    rubric = models.ForeignKey(
        RepertoryRubric,
        on_delete=models.PROTECT,
        related_name="appointment_selections",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["appointment", "rubric"],
                name="unique_rubric_per_appointment",
            )
        ]

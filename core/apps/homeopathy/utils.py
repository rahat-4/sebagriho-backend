from django.db import transaction
from django.db.models import Max

from apps.organizations.models import Organization

MIN_PATIENT_SERIAL = 100000


def get_homeopathic_patient_slug(instance) -> str:
    return f"{instance.user.get_full_name()}-{instance.serial_number}"


def get_homeopathic_appointment_slug(instance):
    return f"{instance.homeopathic_patient.user.get_full_name()}-{instance.organization.name}-{instance.homeopathic_patient.serial_number}"


def get_medicine_media_path_prefix(instance, filename):
    return f"medicines/{instance.organization.uid}/{filename}"


def get_appointment_file_path(instance, filename):
    return f"appointments/{instance.organization.uid}/{filename}"


def get_patient_file_path(instance, filename):
    return f"patients/{instance.organization.uid}/{filename}"


def get_patient_serial_number(organization):
    from apps.homeopathy.models import HomeopathicPatient

    organization = Organization.objects.select_for_update().get(pk=organization.pk)

    last_serial = HomeopathicPatient.objects.filter(
        organization=organization
    ).aggregate(max_serial=Max("serial_number"))["max_serial"]

    if last_serial is None:
        return MIN_PATIENT_SERIAL

    return max(last_serial + 1, MIN_PATIENT_SERIAL)

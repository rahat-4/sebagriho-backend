from django.db import transaction

from apps.organizations.models import Organization


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


def get_next_patient_serial(organization):
    with transaction.atomic():
        organization = Organization.objects.select_for_update().get(pk=organization.pk)
        organization.homeopathic_patient_serial += 1
        organization.save(update_fields=["homeopathic_patient_serial"])

        return organization.homeopathic_patient_serial

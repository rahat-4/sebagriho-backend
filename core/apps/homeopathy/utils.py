def get_homeopathic_patient_slug(instance) -> str:
    return f"{instance.user.get_full_name()}-{instance.serial_number}"


def get_homeopathic_appointment_slug(instance):
    return f"{instance.patient.user.get_full_name()}-{instance.organization.name}-{instance.serial_number}"


def get_medicine_media_path_prefix(instance, filename):
    return f"medicines/{instance.organization.uid}/{filename}"


def get_appointment_file_path(instance, filename):
    return f"appointments/{instance.organization.uid}/{filename}"


def get_patient_file_path(instance, filename):
    return f"patients/{instance.organization.uid}/{filename}"

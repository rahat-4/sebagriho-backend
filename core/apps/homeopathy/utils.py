def get_homeopathic_patient_slug(instance) -> str:
    return f"{instance.user.get_full_name()}-{instance.serial_number}"


import random


def get_homeopathic_appointment_slug(instance):
    return f"{instance.patient.user.get_full_name()}-{instance.organization.name}-{instance.serial_number}"

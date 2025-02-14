import random

def get_appointment_slug(instance):
    return f"{instance.patient.user.get_full_name()}-{instance.organization.name}-{instance.serial_number}"


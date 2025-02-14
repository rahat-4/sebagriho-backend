def get_patient_slug(instance)->str:
    return f"{instance.user.get_full_name()}-{instance.serial_number}"
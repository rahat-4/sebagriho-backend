import os
import random
import uuid


def unique_number_generator(instance) -> int:
    model = instance.__class__
    unique_number = random.randint(111111, 999999)

    while model.objects.filter(serial_number=unique_number).exists():
        unique_number_generator(instance)

    return unique_number


def get_attachment_file_path(instance, filename):
    extension = os.path.splitext(filename)[1].lower()

    return (
        f"organizations/"
        f"{instance.organization.uid}/"
        f"attachments/"
        f"{instance.content_type.model}/"
        f"{instance.object_id}/"
        f"{uuid.uuid4().hex}{extension}"
    )

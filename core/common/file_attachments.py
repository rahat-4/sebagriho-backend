from django.contrib.contenttypes.models import ContentType

from .models import Attachment


def create_attachments(content_object, files, organization, uploaded_by):
    for file in files:
        Attachment.objects.create(
            file=file,
            name=file.name,
            organization=organization,
            uploaded_by=uploaded_by,
            content_object=content_object,
        )


def delete_attachments(content_object, uids, organization):
    content_type = ContentType.objects.get_for_model(content_object)

    attachments = Attachment.objects.filter(
        uid__in=uids,
        organization=organization,
        content_type=content_type,
        object_id=content_object.pk,
    )

    for attachment in attachments:
        # deletes the file from storage too, not just the DB row
        attachment.file.delete(save=False)
        attachment.delete()

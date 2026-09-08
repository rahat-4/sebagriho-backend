from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers

from apps.organizations.models import OrganizationMember
from apps.organizations.choices import OrganizationMemberStatus
from apps.homeopathy.models import (
    HomeopathicPatient,
    HomeopathicAppointment,
    HomeopathicMedicine,
)


from common.models import Attachment
from common.serializers import AttachmentSimSerializer

User = get_user_model()


class PatientUserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        source="get_full_name",
        read_only=True,
    )

    class Meta:
        model = User
        fields = [
            "uid",
            "avatar",
            "name",
            "first_name",
            "last_name",
            "phone",
            "email",
            "gender",
            "date_of_birth",
        ]
        read_only_fields = [
            "uid",
            "avatar",
            "name",
        ]


class HomeopathicPatientSerializer(serializers.ModelSerializer):
    user = PatientUserSerializer()
    upload_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
    )
    files = AttachmentSimSerializer(
        source="attachments",
        many=True,
        read_only=True,
    )

    class Meta:
        model = HomeopathicPatient
        fields = [
            "uid",
            "serial_number",
            "slug",
            "status",
            "old_serial_number",
            "relative_phone",
            "address",
            "age",
            "miasm_type",
            "case_history",
            "habits",
            "user",
            "upload_files",
            "files",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "uid",
            "serial_number",
            "slug",
            "files",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        files = validated_data.pop("upload_files", [])

        request = self.context["request"]
        organization = request.organization

        user = User.objects.create_user(**user_data)

        patient = HomeopathicPatient.objects.create(
            user=user,
            organization=organization,
            **validated_data,
        )

        self._create_attachments(
            patient=patient,
            files=files,
            organization=organization,
            uploaded_by=request.user,
        )

        return patient

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)
        files = validated_data.pop("upload_files", [])

        # Update User
        if user_data:
            user = instance.user

            for field, value in user_data.items():
                setattr(user, field, value)

            user.save()

        # Update Patient
        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()

        # Add new attachments
        self._create_attachments(
            patient=instance,
            files=files,
            organization=instance.organization,
            uploaded_by=self.context["request"].user,
        )

        return instance

    def _create_attachments(
        self,
        patient,
        files,
        organization,
        uploaded_by,
    ):
        for file in files:
            Attachment.objects.create(
                file=file,
                name=file.name,
                organization=organization,
                uploaded_by=uploaded_by,
                content_object=patient,
            )


class HomeopathicAppointmentSerializer(serializers.ModelSerializer):
    patient_uid = serializers.UUIDField(
        write_only=True,
        required=True,
    )

    patient_name = serializers.CharField(
        source="homeopathic_patient.user.get_full_name",
        read_only=True,
    )

    medicine_uids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
    )

    files = AttachmentSimSerializer(
        source="attachments",
        many=True,
        read_only=True,
    )

    upload_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = HomeopathicAppointment
        fields = [
            "uid",
            "slug",
            "symptoms",
            "treatment_effectiveness",
            "status",
            "patient_uid",
            "patient_name",
            "medicine_uids",
            "files",
            "upload_files",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "uid",
            "slug",
            "patient_name",
            "files",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        request = self.context["request"]
        organization = request.organization

        # Patient
        patient_uid = attrs.pop("patient_uid", None)

        if patient_uid is not None:
            try:
                patient = HomeopathicPatient.objects.get(
                    uid=patient_uid,
                    organization=organization,
                )
            except HomeopathicPatient.DoesNotExist:
                raise serializers.ValidationError(
                    {"patient_uid": ("Patient does not belong to this organization.")}
                )

            attrs["homeopathic_patient"] = patient

        # Medicines
        medicine_uids = attrs.pop("medicine_uids", None)

        if medicine_uids is not None:
            medicines = HomeopathicMedicine.objects.filter(
                uid__in=medicine_uids,
                organization=organization,
            )

            if medicines.count() != len(set(medicine_uids)):
                raise serializers.ValidationError(
                    {
                        "medicine_uids": (
                            "One or more medicines do not belong "
                            "to this organization."
                        )
                    }
                )

            attrs["_medicines"] = medicines

        return attrs

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["patient_uid"] = str(instance.homeopathic_patient.uid)

        representation["medicine_uids"] = [
            str(medicine.uid) for medicine in instance.medicines.all()
        ]

        return representation

    def create(self, validated_data):
        medicines = validated_data.pop("_medicines", None)
        upload_files = validated_data.pop("upload_files", [])

        organization = self.context["request"].organization

        appointment = HomeopathicAppointment.objects.create(
            organization=organization,
            **validated_data,
        )

        if medicines is not None:
            appointment.medicines.set(medicines)

        self._create_attachments(
            appointment,
            upload_files,
            organization,
        )

        return appointment

    def update(self, instance, validated_data):
        medicines = validated_data.pop("_medicines", None)
        upload_files = validated_data.pop("upload_files", [])

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()

        if medicines is not None:
            instance.medicines.set(medicines)

        if upload_files:
            self._create_attachments(
                instance,
                upload_files,
                instance.organization,
            )

        return instance

    def _create_attachments(self, appointment, files, organization):
        if not files:
            return

        content_type = ContentType.objects.get_for_model(HomeopathicAppointment)

        request = self.context.get("request")

        for file in files:
            Attachment.objects.create(
                file=file,
                name=file.name,
                uploaded_by=request.user if request else None,
                organization=organization,
                content_type=content_type,
                object_id=appointment.pk,
            )


class HomeopathicMedicineSerializer(serializers.ModelSerializer):
    files = AttachmentSimSerializer(
        source="attachments",
        many=True,
        read_only=True,
    )

    upload_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = HomeopathicMedicine
        fields = [
            "uid",
            "avatar",
            "name",
            "power",
            "expiration_date",
            "is_available",
            "manufacturer",
            "total_quantity",
            "unit_price",
            "description",
            "batch_number",
            "status",
            "files",
            "upload_files",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "uid",
            "files",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        upload_files = validated_data.pop("upload_files", [])

        request = self.context["request"]
        organization = request.organization

        medicine = HomeopathicMedicine.objects.create(
            organization=organization,
            **validated_data,
        )

        self._create_attachments(
            medicine,
            upload_files,
            organization,
        )

        return medicine

    def update(self, instance, validated_data):
        upload_files = validated_data.pop("upload_files", [])

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()

        if upload_files:
            self._create_attachments(
                instance,
                upload_files,
                instance.organization,
            )

        return instance

    def _create_attachments(self, medicine, files, organization):
        if not files:
            return

        content_type = ContentType.objects.get_for_model(HomeopathicMedicine)

        request = self.context.get("request")

        for file in files:
            Attachment.objects.create(
                file=file,
                name=file.name,
                uploaded_by=request.user if request else None,
                organization=organization,
                content_type=content_type,
                object_id=medicine.pk,
            )

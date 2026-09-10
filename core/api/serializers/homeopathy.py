from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from rest_framework import serializers

from apps.homeopathy.models import (
    HomeopathicPatient,
    HomeopathicAppointment,
    HomeopathicMedicine,
)
from apps.homeopathy.utils import get_next_patient_serial


from common.models import Attachment
from common.serializers import (
    AttachmentSimSerializer,
    UserSlimSerializer,
    MedicineSlimSerializer,
)

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

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop("user")
        files = validated_data.pop("upload_files", [])

        request = self.context["request"]
        organization = request.organization

        # Generate organization-scoped patient serial number
        serial_number = get_next_patient_serial(organization)

        user = User.objects.create_user(
            **user_data,
        )

        patient = HomeopathicPatient.objects.create(
            user=user,
            organization=organization,
            serial_number=serial_number,
            **validated_data,
        )

        self._create_attachments(
            patient=patient,
            files=files,
            organization=organization,
            uploaded_by=request.user,
        )

        return patient

    @transaction.atomic
    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)
        files = validated_data.pop("upload_files", [])

        # -------------------------
        # Update User
        # -------------------------
        if user_data:
            user = instance.user

            for field, value in user_data.items():
                setattr(user, field, value)

            user.save()

        # -------------------------
        # Update Patient
        # -------------------------
        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()

        # -------------------------
        # Add attachments
        # -------------------------
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
    patient = serializers.UUIDField(
        write_only=True,
        required=True,
    )

    medicine_uids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
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

    medicines = MedicineSlimSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = HomeopathicAppointment
        fields = [
            "uid",
            "slug",
            "symptoms",
            "treatment_effectiveness",
            "status",
            "patient",
            "medicines",
            "medicine_uids",
            "files",
            "upload_files",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "uid",
            "slug",
            "files",
            "medicines",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        request = self.context["request"]
        organization = request.organization

        errors = {}

        # Patient
        patient_uid = attrs.pop("patient", None)

        if patient_uid is not None:
            try:
                patient = HomeopathicPatient.objects.get(
                    uid=patient_uid,
                    organization=organization,
                )
                attrs["homeopathic_patient"] = patient

            except HomeopathicPatient.DoesNotExist:
                errors["patient"] = "Patient does not belong to this organization."

        # Medicines
        medicine_uids = attrs.pop("medicine_uids", None)

        if medicine_uids is not None:
            medicine_uids = list(set(medicine_uids))

            medicines = HomeopathicMedicine.objects.filter(
                uid__in=medicine_uids,
                organization=organization,
            )

            if medicines.count() != len(medicine_uids):
                errors["medicine_uids"] = (
                    "One or more medicines do not belong " "to this organization."
                )
            else:
                attrs["_medicines"] = list(medicines)

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

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

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["patient"] = UserSlimSerializer(
            instance.homeopathic_patient.user
        ).data

        return representation

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

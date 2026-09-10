from django.contrib.auth import get_user_model
from django.db import transaction

from rest_framework import serializers

from apps.homeopathy.models import (
    HomeopathicPatient,
    HomeopathicAppointment,
    HomeopathicMedicine,
)
from apps.homeopathy.utils import get_next_patient_serial


from common.serializers import (
    AttachmentSimSerializer,
    UserSlimSerializer,
    MedicineSlimSerializer,
)
from common.file_attachments import create_attachments, delete_attachments

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
    remove_files = serializers.ListField(
        child=serializers.UUIDField(),
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
            "files",
            "upload_files",
            "remove_files",
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
        upload_files = validated_data.pop("upload_files", [])

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

        if upload_files:
            create_attachments(
                patient=patient,
                files=upload_files,
                organization=organization,
                uploaded_by=request.user,
            )

        return patient

    @transaction.atomic
    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)
        upload_files = validated_data.pop("upload_files", [])
        remove_files = validated_data.pop("remove_files", [])

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

        if upload_files:
            create_attachments(
                content_object=instance,
                files=upload_files,
                organization=instance.organization,
                uploaded_by=self.context["request"].user,
            )

        if remove_files:
            delete_attachments(
                content_object=instance,
                uids=remove_files,
                organization=instance.organization,
            )

        return instance


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
    remove_files = serializers.ListField(
        child=serializers.UUIDField(),
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
            "remove_files",
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

        if upload_files:
            create_attachments(
                content_object=appointment,
                files=upload_files,
                organization=organization,
                uploaded_by=self.context["request"].user,
            )

        return appointment

    def update(self, instance, validated_data):
        medicines = validated_data.pop("_medicines", None)
        upload_files = validated_data.pop("upload_files", [])
        remove_files = validated_data.pop("remove_files", [])

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()

        if medicines is not None:
            instance.medicines.set(medicines)

        if upload_files:
            create_attachments(
                content_object=instance,
                files=upload_files,
                organization=instance.organization,
                uploaded_by=self.context["request"].user,
            )

        if remove_files:
            delete_attachments(
                content_object=instance,
                uids=remove_files,
                organization=instance.organization,
            )

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["patient"] = UserSlimSerializer(
            instance.homeopathic_patient.user
        ).data

        return representation


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
    remove_files = serializers.ListField(
        child=serializers.UUIDField(),
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
            "remove_files",
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

        if upload_files:
            create_attachments(
                content_object=medicine,
                files=upload_files,
                organization=organization,
                uploaded_by=self.context["request"].user,
            )

        return medicine

    def update(self, instance, validated_data):
        upload_files = validated_data.pop("upload_files", [])
        remove_files = validated_data.pop("remove_files", [])

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()

        if upload_files:
            create_attachments(
                content_object=instance,
                files=upload_files,
                organization=instance.organization,
                uploaded_by=self.context["request"].user,
            )

        if remove_files:
            delete_attachments(
                content_object=instance,
                uids=remove_files,
                organization=instance.organization,
            )

        return instance

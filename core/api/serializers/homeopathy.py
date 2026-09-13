from django.contrib.auth import get_user_model
from django.db import transaction

from rest_framework import serializers

from apps.homeopathy.models import (
    HomeopathicPatient,
    HomeopathicAppointment,
    HomeopathicMedicine,
    HomeopathicPrescription,
)
from apps.homeopathy.utils import get_patient_serial_number


from common.serializers import (
    AttachmentSimSerializer,
    HomeopathicPatientSlimSerializer,
    MedicineSlimSerializer,
)
from common.file_attachments import create_attachments, delete_attachments

User = get_user_model()


class HomeopathicDashboardSerializer(serializers.Serializer):
    from rest_framework import serializers


class HomeopathicDashboardSerializer(serializers.Serializer):
    summary = serializers.DictField()
    patient_growth = serializers.ListField()
    appointment_growth = serializers.ListField()
    appointment_status = serializers.ListField()
    patient_status = serializers.ListField()
    medicine_status = serializers.ListField()
    top_medicines = serializers.ListField()


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
        serial_number = get_patient_serial_number(organization)

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


class HomeopathicPrescriptionSerializer(serializers.ModelSerializer):
    medicine = serializers.UUIDField(write_only=True)
    medicine_details = MedicineSlimSerializer(
        source="medicine",
        read_only=True,
    )

    class Meta:
        model = HomeopathicPrescription
        fields = [
            "uid",
            "medicine",
            "medicine_details",
            "dosage",
            "frequency",
            "duration",
            "meal_timing",
            "instructions",
        ]
        read_only_fields = [
            "uid",
            "medicine_details",
        ]

    def validate_medicine(self, value):
        organization = self.context["request"].organization

        try:
            return HomeopathicMedicine.objects.get(
                uid=value,
                organization=organization,
            )
        except HomeopathicMedicine.DoesNotExist:
            raise serializers.ValidationError(
                "Medicine does not belong to this organization."
            )


class HomeopathicAppointmentSerializer(serializers.ModelSerializer):
    patient = serializers.UUIDField(
        write_only=True,
        required=True,
    )
    appointment_prescription = HomeopathicPrescriptionSerializer(
        many=True,
        required=False,
    )
    remove_medicine_uids = serializers.ListField(
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

    class Meta:
        model = HomeopathicAppointment
        fields = [
            "uid",
            "slug",
            "symptoms",
            "treatment_effectiveness",
            "status",
            "patient",
            "appointment_prescription",
            "remove_medicine_uids",
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
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        request = self.context["request"]
        organization = request.organization

        # --------------------------------
        # Patient validation
        # --------------------------------
        patient_uid = attrs.pop("patient", None)

        if patient_uid is not None:
            try:
                patient = HomeopathicPatient.objects.get(
                    uid=patient_uid,
                    organization=organization,
                )
            except HomeopathicPatient.DoesNotExist:
                raise serializers.ValidationError(
                    {"patient": ("Patient does not belong to this organization.")}
                )

            attrs["homeopathic_patient"] = patient

        # --------------------------------
        # Remove medicine UUIDs
        # --------------------------------
        remove_medicine_uids = attrs.get(
            "remove_medicine_uids",
            [],
        )

        if remove_medicine_uids:
            attrs["remove_medicine_uids"] = list(set(remove_medicine_uids))

        return attrs

    def create(self, validated_data):
        prescription_data = validated_data.pop(
            "appointment_prescription",
            [],
        )
        # Not applicable during create
        validated_data.pop(
            "remove_medicine_uids",
            [],
        )
        upload_files = validated_data.pop(
            "upload_files",
            [],
        )
        organization = self.context["request"].organization

        # --------------------------------
        # Create appointment
        # --------------------------------
        appointment = HomeopathicAppointment.objects.create(
            organization=organization,
            **validated_data,
        )

        # --------------------------------
        # Create prescription
        # --------------------------------
        prescription = []

        for prescription_data in prescription_data:
            prescription.append(
                HomeopathicPrescription(
                    appointment=appointment,
                    **prescription_data,
                )
            )

        if prescription:
            HomeopathicPrescription.objects.bulk_create(prescription)

        # --------------------------------
        # Upload files
        # --------------------------------
        if upload_files:
            create_attachments(
                content_object=appointment,
                files=upload_files,
                organization=organization,
                uploaded_by=self.context["request"].user,
            )

        return appointment

    def update(self, instance, validated_data):
        prescription_data = validated_data.pop(
            "appointment_prescription",
            None,
        )
        remove_medicine_uids = validated_data.pop(
            "remove_medicine_uids",
            [],
        )
        upload_files = validated_data.pop(
            "upload_files",
            [],
        )
        remove_files = validated_data.pop(
            "remove_files",
            [],
        )

        # --------------------------------
        # Update appointment fields
        # --------------------------------
        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()

        # --------------------------------
        # Remove one/multiple medicines
        # --------------------------------
        if remove_medicine_uids:
            HomeopathicPrescription.objects.filter(
                appointment=instance,
                medicine__uid__in=remove_medicine_uids,
            ).delete()

        # --------------------------------
        # Create / update prescription
        # --------------------------------
        if prescription_data is not None:
            for prescription_data in prescription_data:
                medicine = prescription_data["medicine"]

                HomeopathicPrescription.objects.update_or_create(
                    appointment=instance,
                    medicine=medicine,
                    defaults={
                        "dosage": prescription_data.get("dosage"),
                        "frequency": prescription_data.get("frequency"),
                        "duration": prescription_data.get("duration"),
                        "meal_timing": prescription_data.get("meal_timing"),
                        "instructions": prescription_data.get("instructions"),
                    },
                )

        # --------------------------------
        # Upload files
        # --------------------------------
        if upload_files:
            create_attachments(
                content_object=instance,
                files=upload_files,
                organization=instance.organization,
                uploaded_by=self.context["request"].user,
            )

        # --------------------------------
        # Remove files
        # --------------------------------
        if remove_files:
            delete_attachments(
                content_object=instance,
                uids=remove_files,
                organization=instance.organization,
            )

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["patient"] = HomeopathicPatientSlimSerializer(
            instance.homeopathic_patient, context=self.context
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

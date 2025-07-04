from django.contrib.auth import get_user_model
from django.db import transaction

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.homeopathy.models import (
    HomeopathicPatient,
    HomeopathicAppointment,
    HomeopathicMedicine,
)

from apps.organizations.models import Organization, OrganizationMember

from common.serializers import OrganizationSlimSerializer, UserSlimSerializer

User = get_user_model()


class HomeopathicProfileDetailSerializer(serializers.ModelSerializer):
    organization = OrganizationSlimSerializer()
    user = UserSlimSerializer()

    class Meta:
        model = OrganizationMember
        fields = ["uid", "organization", "user", "created_at", "updated_at"]


class HomeopathicPatientListSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name", allow_blank=True)
    name = serializers.SerializerMethodField()
    phone = serializers.CharField(source="user.phone")
    avatar = serializers.ImageField(
        source="user.avatar", allow_null=True, required=False
    )
    gender = serializers.CharField(
        source="user.gender", allow_blank=True, required=False
    )
    blood_group = serializers.CharField(
        source="user.blood_group", allow_blank=True, required=False
    )

    class Meta:
        model = HomeopathicPatient
        fields = [
            "uid",
            "avatar",
            "name",
            "first_name",
            "last_name",
            "phone",
            "age",
            "gender",
            "blood_group",
            "serial_number",
            "old_serial_number",
            "relative_phone",
            "address",
            "miasm_type",
            "case_history",
            "habits",
            "patient_file",
            "status",
            "slug",
            "created_at",
            "updated_at",
        ]

    def get_name(self, obj):
        return obj.user.get_full_name()

    def validate_phone(self, value):
        user = User.objects.filter(phone=value).exists()
        if user:
            raise serializers.ValidationError(
                "This phone number is already registered."
            )

        return value

    def create(self, validated_data):
        with transaction.atomic():
            organization_uid = self.context["view"].kwargs.get("organization_uid")
            user = validated_data.pop("user")

            user_data = {
                "first_name": user["first_name"],
                "last_name": user.get("last_name", ""),
                "phone": user["phone"],
                "avatar": user.get("avatar"),
                "gender": user.get("gender"),
                "blood_group": user.get("blood_group"),
            }
            organization = Organization.objects.filter(uid=organization_uid).first()

            if not organization:
                raise ValidationError("Organization not found!")

            user = User.objects.create_user(**user_data)
            patient = HomeopathicPatient.objects.create(
                user=user, organization=organization, **validated_data
            )

            return patient


class HomeopathicPatientDetailSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    first_name = serializers.CharField(
        source="user.first_name", allow_blank=True, required=False
    )
    last_name = serializers.CharField(
        source="user.last_name", allow_blank=True, required=False
    )
    phone = serializers.CharField(source="user.phone", allow_blank=True, required=False)
    avatar = serializers.ImageField(
        source="user.avatar", allow_null=True, required=False
    )
    gender = serializers.CharField(
        source="user.gender", allow_blank=True, required=False
    )
    blood_group = serializers.CharField(
        source="user.blood_group", allow_blank=True, required=False
    )

    class Meta:
        model = HomeopathicPatient
        fields = [
            "uid",
            "avatar",
            "name",
            "first_name",
            "last_name",
            "phone",
            "age",
            "gender",
            "blood_group",
            "serial_number",
            "old_serial_number",
            "relative_phone",
            "address",
            "miasm_type",
            "case_history",
            "habits",
            "status",
            "slug",
            "created_at",
            "updated_at",
        ]

    def get_name(self, obj):
        return obj.user.get_full_name()

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)
        if user_data:
            user = instance.user
            user.first_name = user_data.get("first_name", user.first_name)
            user.last_name = user_data.get("last_name", user.last_name)
            user.phone = user_data.get("phone", user.phone)
            user.avatar = user_data.get("avatar", user.avatar)
            user.gender = user_data.get("gender", user.gender)
            user.save()

        instance.age = validated_data.get("age", instance.age)
        instance.relative_phone = validated_data.get(
            "relative_phone", instance.relative_phone
        )
        instance.address = validated_data.get("address", instance.address)
        instance.miasm_type = validated_data.get("miasm_type", instance.miasm_type)
        instance.case_history = validated_data.get(
            "case_history", instance.case_history
        )
        instance.habits = validated_data.get("habits", instance.habits)
        instance.status = validated_data.get("status", instance.status)

        instance.save()
        return instance


class HomeopathicPatientAppointmentListSerializer(serializers.ModelSerializer):
    medicines = serializers.SlugRelatedField(
        many=True,
        queryset=HomeopathicMedicine.objects.all(),
        slug_field="uid",
        allow_empty=True,
        allow_null=True,
        required=False,
    )

    class Meta:
        model = HomeopathicAppointment
        fields = [
            "uid",
            "slug",
            "symptoms",
            "treatment_effectiveness",
            "appointment_file",
            "medicines",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        medicines = validated_data.pop("medicines", [])

        organization_uid = self.context["view"].kwargs.get("organization_uid")
        patient_uid = self.context["view"].kwargs.get("patient_uid")

        organization = Organization.objects.filter(uid=organization_uid).first()
        patient = HomeopathicPatient.objects.filter(uid=patient_uid).first()

        appointment = HomeopathicAppointment.objects.create(
            organization=organization, homeopathic_patient=patient, **validated_data
        )

        appointment.medicines.add(*medicines)

        return appointment


class HomeopathicAppointmentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeopathicAppointment
        fields = [
            "uid",
            "slug",
            "symptoms",
            "treatment_effectiveness",
            "homeopathic_patient",
            "organization",
            "created_at",
            "updated_at",
        ]


class HomeopathicMedicineSerializer(serializers.ModelSerializer):
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
            "created_at",
            "updated_at",
        ]

        read_only_fields = ["uid", "created_at", "updated_at"]

from django.contrib.auth import get_user_model
from django.db import transaction

from rest_framework import serializers

from apps.patients.models import Patient

User = get_user_model()


class HomeopathyPatientSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name", allow_blank=True)
    phone = serializers.CharField(source="user.phone")
    avatar = serializers.ImageField(
        source="user.avatar", allow_null=True, required=False
    )

    class Meta:
        model = Patient
        fields = [
            "uid",
            "avatar",
            "first_name",
            "last_name",
            "phone",
            "serial_number",
            "old_serial_number",
            "relative_phone",
            "address",
            "status",
            "slug",
            "created_at",
            "updated_at",
        ]

    def validate_phone(self, value):
        user = User.objects.filter(phone=value).exists()
        if user:
            raise serializers.ValidationError(
                "This phone number is already registered."
            )

        return value

    def create(self, validated_data):
        with transaction.atomic():
            user = validated_data.pop("user")

            user_data = {
                "first_name": user["first_name"],
                "last_name": user.get("last_name", ""),
                "phone": user["phone"],
                "avatar": user.get("avatar"),
            }
            user = User.objects.create_user(**user_data)
            patient = Patient.objects.create(user=user, **validated_data)

            return patient

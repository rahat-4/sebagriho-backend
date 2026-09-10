from rest_framework import serializers

from apps.homeopathy.models import HomeopathicPatient, HomeopathicMedicine


class HomeopathicPatientFilterSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(source="user.avatar", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)

    class Meta:
        model = HomeopathicPatient
        fields = [
            "uid",
            "avatar",
            "first_name",
            "last_name",
            "email",
            "phone",
        ]
        read_only_fields = fields


class HomeopathicMedicineFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeopathicMedicine
        fields = [
            "uid",
            "avatar",
            "name",
            "power",
            "manufacturer",
            "expiration_date",
            "status",
        ]
        read_only_fields = fields

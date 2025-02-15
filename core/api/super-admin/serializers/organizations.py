from django.contrib.auth import get_user_model
from django.db import transaction

from rest_framework import serializers

from apps.organizations.models import Organization
from apps.doctors.models import (
    Achievement,
    Affiliation,
    Degree,
    Department,
    Doctor,
    Specialty,
    LanguageSpoken,
)

from common.serializers import (
    AchievementSlimSerializer,
    AffiliationSlimSerializer,
    DoctorSlimSerializer,
    DegreeSlimSerializer,
    DepartmentSlimSerializer,
    SpecialtySlimSerializer,
    LanguageSpokenSlimSerializer,
    UserSlimSerializer,
)

User = get_user_model()


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"


class OrganizationDoctorListSerializer(serializers.ModelSerializer):
    user = UserSlimSerializer()
    degrees = DegreeSlimSerializer(many=True)
    achievements = AchievementSlimSerializer(many=True)
    affiliations = AffiliationSlimSerializer(many=True)
    departments = serializers.SlugRelatedField(
        many=True,
        slug_field="uid",
        queryset=Department.objects.all(),
        write_only=True,
    )
    specialties = serializers.SlugRelatedField(
        many=True,
        slug_field="uid",
        queryset=Specialty.objects.all(),
        write_only=True,
    )
    languages_spoken = serializers.SlugRelatedField(
        many=True,
        slug_field="uid",
        queryset=LanguageSpoken.objects.all(),
        write_only=True,
    )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        departments = DepartmentSlimSerializer(
            instance.departments.all(), many=True
        ).data
        specialties = SpecialtySlimSerializer(
            instance.specialties.all(), many=True
        ).data
        languages_spoken = LanguageSpokenSlimSerializer(
            instance.languages_spoken.all(), many=True
        ).data

        representation["departments"] = departments
        representation["specialties"] = specialties
        representation["languages_spoken"] = languages_spoken

        return representation

    class Meta:
        model = Doctor
        fields = [
            "uid",
            "user",
            "registration_number",
            "experience",
            "about",
            "appointment_fee",
            "consultation_fee",
            "follow_up_fee",
            "check_up_fee",
            "degrees",
            "specialties",
            "departments",
            "achievements",
            "affiliations",
            "languages_spoken",
            "status",
        ]

    def create(self, validated_data):
        # Use atomic transaction to ensure data integrity
        with transaction.atomic():
            # Extract nested data
            departments = validated_data.pop("departments")
            languages_spoken = validated_data.pop("languages_spoken")
            specialty_instances = validated_data.pop("specialties")
            degrees_data = validated_data.pop("degrees")
            affiliations_data = validated_data.pop("affiliations")
            achievements_data = validated_data.pop("achievements", [])

            # Handle user creation
            user_data = validated_data.pop("user")
            user_data.pop("confirm_password")
            user = User.objects.create(**user_data)

            # Create Doctor instance
            doctor_instance = Doctor.objects.create(user=user, **validated_data)

            # Bulk create many-to-many relations
            degrees = [Degree.objects.get_or_create(**data)[0] for data in degrees_data]
            achievements = [
                Achievement.objects.get_or_create(**data)[0]
                for data in achievements_data
            ]
            affiliations = [
                Affiliation.objects.get_or_create(**data)[0]
                for data in affiliations_data
            ]

            # Add many-to-many relations
            doctor_instance.degrees.add(*degrees)
            doctor_instance.departments.add(*departments)
            doctor_instance.specialties.add(*specialty_instances)
            doctor_instance.achievements.add(*achievements)
            doctor_instance.affiliations.add(*affiliations)
            doctor_instance.languages_spoken.add(*languages_spoken)

            return doctor_instance

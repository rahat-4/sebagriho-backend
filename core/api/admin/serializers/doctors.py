from django.contrib.auth import get_user_model
from django.db import transaction

from rest_framework import serializers

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


class CompleteProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "avatar",
            "nid",
            "nid_front",
            "nid_back",
        ]


class AdminDoctorListCreateSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="uid", queryset=User.objects.all(), write_only=True
    )
    complete_profile = CompleteProfileSerializer(write_only=True)
    degrees = DegreeSlimSerializer(many=True, required=False)
    achievements = AchievementSlimSerializer(many=True, required=False)
    affiliations = AffiliationSlimSerializer(many=True, required=False)
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
        representation["user"] = UserSlimSerializer(instance.user).data
        representation["departments"] = DepartmentSlimSerializer(
            instance.departments.all(), many=True
        ).data
        representation["specialties"] = SpecialtySlimSerializer(
            instance.specialties.all(), many=True
        ).data
        representation["languages_spoken"] = LanguageSpokenSlimSerializer(
            instance.languages_spoken.all(), many=True
        ).data

        return representation

    class Meta:
        model = Doctor
        fields = [
            "uid",
            "user",
            "complete_profile",
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
        with transaction.atomic():
            # Extract related fields
            user = validated_data.pop("user", {})
            complete_profile_data = validated_data.pop("complete_profile", {})
            departments = validated_data.pop("departments", [])
            specialties = validated_data.pop("specialties", [])
            languages_spoken = validated_data.pop("languages_spoken", [])
            degrees_data = validated_data.pop("degrees", [])
            affiliations_data = validated_data.pop("affiliations", [])
            achievements_data = validated_data.pop("achievements", [])

            # Handle user creation
            user.avatar = complete_profile_data.get("avatar")
            user.nid = complete_profile_data.get("nid")
            user.nid_front = complete_profile_data.get("nid_front")
            user.nid_back = complete_profile_data.get("nid_back")
            user.save()

            # Create doctor
            doctor_instance = Doctor.objects.create(user=user, **validated_data)

            # Bulk create degrees, achievements, affiliations (if not existing)
            degrees = [Degree.objects.get_or_create(**data)[0] for data in degrees_data]
            achievements = [
                Achievement.objects.get_or_create(**data)[0]
                for data in achievements_data
            ]
            affiliations = [
                Affiliation.objects.get_or_create(**data)[0]
                for data in affiliations_data
            ]

            # Use .set() instead of .add() for better efficiency
            doctor_instance.departments.set(departments)
            doctor_instance.specialties.set(specialties)
            doctor_instance.languages_spoken.set(languages_spoken)
            doctor_instance.degrees.set(degrees)
            doctor_instance.achievements.set(achievements)
            doctor_instance.affiliations.set(affiliations)

            return doctor_instance

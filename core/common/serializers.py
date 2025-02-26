from django.contrib.auth import get_user_model

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

User = get_user_model()


class UserSlimSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "uid",
            "first_name",
            "last_name",
            "phone",
            "email",
            "gender",
            "nid",
            "nid_front",
            "nid_back",
            "avatar",
            "blood_group",
            "date_of_birth",
        ]


class DegreeSlimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Degree
        fields = ["uid", "name", "institute", "result", "passing_year", "country"]


class DepartmentSlimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["uid", "name", "description"]


class SpecialtySlimSerializer(serializers.ModelSerializer):
    department = DepartmentSlimSerializer()

    class Meta:
        model = Specialty
        fields = ["uid", "name", "department"]


class AchievementSlimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ["uid", "name", "source", "year"]


class AffiliationSlimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Affiliation
        fields = ["uid", "title", "hospital_name", "status"]


class LanguageSpokenSlimSerializer(serializers.ModelSerializer):
    class Meta:
        model = LanguageSpoken
        fields = ["uid", "language"]


class DoctorSlimSerializer(serializers.ModelSerializer):
    user = UserSlimSerializer()
    department = DepartmentSlimSerializer()

    class Meta:
        model = Doctor
        fields = ["user", "about", "department", "experience"]

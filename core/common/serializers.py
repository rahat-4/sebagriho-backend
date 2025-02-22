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
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone",
            "email",
            "gender",
            "password",
            "confirm_password",
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

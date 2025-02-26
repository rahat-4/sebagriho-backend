from django.contrib.auth import get_user_model

from rest_framework import serializers

from apps.patients.models import Patient

User = get_user_model()


class PatientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = "__all__"

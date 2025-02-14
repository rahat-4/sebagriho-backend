from django.core.management.base import BaseCommand

from apps.doctors.models import Department, Specialty
from apps.doctors.choices import DepartmentType

from ..data.specialities import MEDICAL_SPECIALTIES, DENTAL_SPECIALTIES


class Command(BaseCommand):
    help = "Populate specialties for existing departments."

    def create_specialty(self, name, department):
        """Helper method to create or get a specialty."""
        specialty, created = Specialty.objects.get_or_create(name=name, department=department)
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created specialty: {name} in {department.name}"))
        else:
            self.stdout.write(f"Specialty already exists: {name} in {department.name}")

    def handle(self, *args, **kwargs):
        """Main method to handle specialty creation for departments."""
        # Process MEDICAL specialties
        self.create_specialties(MEDICAL_SPECIALTIES, DepartmentType.MEDICAL)

        # Process DENTAL specialties
        self.create_specialties(DENTAL_SPECIALTIES, DepartmentType.DENTAL)

    def create_specialties(self, specialties_data, department_type):
        """Helper method to create specialties for each department."""
        for department_name, specialties in specialties_data.items():
            try:
                department = Department.objects.filter(name=department_name, department_type=department_type).first()
                for specialty_data in specialties:
                    self.create_specialty(specialty_data["name"], department)
            except Department.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Department does not exist: {department_name}"))
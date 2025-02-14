from django.core.management.base import BaseCommand

from apps.doctors.models import Department
from apps.doctors.choices import DepartmentType

from ..data.departments import MEDICAL_DEPARTMENTS, DENTAL_DEPARTMENTS


class Command(BaseCommand):
    help = "Populate departments and sub-departments."

    def create_department(self, name, description, department_type, parent=None):
        """Helper method to create or get a department and its sub-departments."""
        department, created = Department.objects.get_or_create(
            name=name,
            defaults={"description": description, "department_type": department_type, "parent": parent}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created department: {name}"))
        else:
            self.stdout.write(f"Department already exists: {name}")
        return department

    def handle(self, *args, **kwargs):
        """Main method to handle department and sub-department creation."""
        # Process MEDICAL departments
        self.create_departments(MEDICAL_DEPARTMENTS, DepartmentType.MEDICAL)

        # Process DENTAL departments
        self.create_departments(DENTAL_DEPARTMENTS, DepartmentType.DENTAL)

    def create_departments(self, departments_data, department_type):
        """Helper method to create departments and sub-departments."""
        for dept_data in departments_data:
            name = dept_data["name"]
            description = dept_data.get("description", "")
            sub_departments = dept_data.get("sub_departments", [])

            # Create main department
            department = self.create_department(name, description, department_type)

            # Create sub-departments
            for sub_data in sub_departments:
                sub_name = sub_data["name"]
                sub_description = sub_data.get("description", "")
                self.create_department(sub_name, sub_description, department_type, parent=department)

from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Run multiple management commands to generate all credentials."

    def handle(self, *args, **options):
        # Run cleancache command
        self.stdout.write(self.style.SUCCESS("Running cleancache command..."))
        call_command("cleancache")

        # Run makemigrations command
        self.stdout.write(self.style.SUCCESS("Running makemigrations command..."))
        call_command("makemigrations")

        # Run migrate command
        self.stdout.write(self.style.SUCCESS("Running migrate command..."))
        call_command("migrate")

        # Run createsuperuser command
        self.stdout.write(self.style.SUCCESS("Running createsuperuser command..."))
        call_command("create_superuser")

        # Run create_departments command
        self.stdout.write(self.style.SUCCESS("Running create_departments command..."))
        call_command("create_departments")

        # Run create_specialities command
        self.stdout.write(self.style.SUCCESS("Running create_specialities command..."))
        call_command("create_specialities")

        # # Run create_languages command
        # self.stdout.write(self.style.SUCCESS("Running create_languages command..."))
        # call_command("create_languages")

        self.stdout.write(self.style.SUCCESS("All commands executed successfully!"))
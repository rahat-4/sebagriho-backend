from django.core.management.base import BaseCommand, CommandError

from apps.authentication.models import User


class Command(BaseCommand):
    help = "Create a superuser"

    def handle(self, *args, **kwargs):
        phone = "+8801521507316"
        password = "admin"

        try:
            if User.objects.filter(phone=phone).exists():
                raise CommandError("A user with this email already exists.")

            User.objects.create_superuser(phone=phone, password=password)
            self.stdout.write(self.style.SUCCESS("Successfully created superuser"))
        except Exception as e:
            raise CommandError(f"Error creating superuser: {e}")
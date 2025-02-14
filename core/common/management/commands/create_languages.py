# import pycountry

# from django.core.management.base import BaseCommand

# from apps.doctor.models import LanguageSpoken


# class Command(BaseCommand):
#     def handle(self, *args, **options):
#         """Main method to handle language creation."""
#         for language in pycountry.languages:
#             language, created = LanguageSpoken.objects.get_or_create(language=language.name)

#             if created:
#                 self.stdout.write(self.style.SUCCESS("Languages created successfully!"))
#             else:
#                 self.stdout.write(f"Language already exists: {language.language}")

        
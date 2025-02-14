import os
import shutil

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Remove __pycache__ directories, migration files except __init__.py, and db.sqlite3"

    def handle(self, *args, **kwargs):
        # Define the root directory for the project
        root_dir = os.getcwd()

        # Walk through the directory tree
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Skip env directories
            if "env" in dirnames:
                dirnames.remove("env")
                
            if 'venv' in dirnames:
                dirnames.remove('venv')

            # Remove __pycache__ directories
            if "__pycache__" in dirnames:
                pycache_path = os.path.join(dirpath, "__pycache__")
                shutil.rmtree(pycache_path)
                self.stdout.write(self.style.SUCCESS(f"Removed: {pycache_path}"))

            # Check if we are in a migrations directory
            if "migrations" in dirpath.split(os.sep):
                for filename in filenames:
                    if filename != "__init__.py" and filename.endswith(".py"):
                        file_path = os.path.join(dirpath, filename)
                        os.remove(file_path)
                        self.stdout.write(self.style.SUCCESS(f"Removed: {file_path}"))

        # Remove db.sqlite3 if it exists
        db_path = os.path.join(root_dir, "db.sqlite3")
        if os.path.exists(db_path):
            os.remove(db_path)
            self.stdout.write(self.style.SUCCESS(f"Removed: {db_path}"))

        self.stdout.write(self.style.SUCCESS("Clean up complete!"))

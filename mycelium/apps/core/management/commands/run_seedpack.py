import importlib.util
from pathlib import Path
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

from apps.core.seedpacks.loader import SEEDPACKS_DIR, get_seed_order

User = get_user_model()

class Command(BaseCommand):
    help = "Clears non-superuser data and loads a named seedpack"

    def add_arguments(self, parser):
        parser.add_argument("pack", help="Name of the seedpack to run")

    def handle(self, *args, **options):
        pack_name = options["pack"]
        seedpack_path = SEEDPACKS_DIR / pack_name
        if not seedpack_path.exists():
            self.stderr.write(self.style.ERROR(f"Seedpack '{pack_name}' not found."))
            return

        self.stdout.write(self.style.NOTICE(f"Loading seedpack '{pack_name}'..."))
        self.clear_data_except_superusers()

        for path in get_seed_order(seedpack_path):
            self.stdout.write(self.style.NOTICE(f"Running {path.name}..."))
            try:
                spec = importlib.util.spec_from_file_location(path.stem, path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "Command"):
                    mod.Command().handle()
                else:
                    self.stderr.write(self.style.WARNING(f"{path.name} missing Command class."))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error running {path.name}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"✅ Seedpack '{pack_name}' completed."))

    def clear_data_except_superusers(self):
        ignore_models = {
            Group,
            Permission,
            ContentType,
        }

        self.stdout.write(self.style.NOTICE("Clearing data (except superusers and system models)..."))

        for model in apps.get_models():
            model_name = f"{model._meta.app_label}.{model.__name__}"

            if model in ignore_models:
                self.stdout.write(f"Skipping {model_name}")
                continue

            try:
                if model == User:
                    deleted, _ = model.objects.exclude(is_superuser=True).delete()
                    self.stdout.write(f"Cleared {deleted} objects from {model_name} (non-superusers only)")
                else:
                    deleted, _ = model.objects.all().delete()
                    self.stdout.write(f"Cleared {deleted} objects from {model_name}")
            except Exception as e:
                self.stderr.write(self.style.WARNING(f"Could not clear {model_name}: {e}"))

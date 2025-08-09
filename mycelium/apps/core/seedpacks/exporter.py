# apps/core/seedpacks/exporter.py
from __future__ import annotations

import io
import json
import re
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Iterable

from django.apps import apps as django_apps
from django.core.management import call_command

# 🔗 Use the same SEEDPACKS_DIR as the loader
from .loader import SEEDPACKS_DIR

_SLUG_RE = re.compile(r"[^a-z0-9\-]+")


def _slugify(name: str) -> str:
    s = (name or "").strip().lower().replace(" ", "-")
    s = _SLUG_RE.sub("", s)
    return s or "seedpack"


def _dump_app_fixture(app_label: str) -> str:
    """
    Dump all models belonging to an app as JSON (including PKs).
    Returns the JSON string (pretty-printed) or "[]" if no rows.
    """
    app_config = django_apps.get_app_config(app_label)
    # Build a stable, explicit model list: app_label.ModelName
    model_labels: list[str] = []
    for model in app_config.get_models():
        model_labels.append(f"{app_label}.{model._meta.model_name}")

    if not model_labels:
        return "[]"

    out = io.StringIO()
    # Use PKs to preserve relations reliably; natural keys work only if
    # all involved models implement them. This is safer across custom apps.
    call_command(
        "dumpdata",
        *model_labels,
        indent=2,
        format="json",
        stdout=out,
    )
    return out.getvalue() or "[]"


def export_seedpack(
    name: str,
    apps: Iterable[str],
    *,
    exported_by: str | None = None,
    include_users: bool = False,
    include_media: bool = False,  # kept for future; noop for now
) -> dict:
    """
    Export selected apps' table rows into a seedpack.
    - Writes fixtures/<app>.json for each app selected.
    - Generates seed_<app>.py that calls loaddata on that JSON.
    - Adds a minimal seed_stub.py so packs are discoverable even if empty.
    - Zips the folder as <slug>.zip next to the folder.

    Returns: {"slug", "dir", "zip"}
    """
    slug = _slugify(name)
    # Ensure folder root exists
    SEEDPACKS_DIR.mkdir(parents=True, exist_ok=True)

    pack_dir = SEEDPACKS_DIR / slug
    if pack_dir.exists():
        shutil.rmtree(pack_dir)
    pack_dir.mkdir(parents=True, exist_ok=True)

    fixtures_dir = pack_dir / "fixtures"
    fixtures_dir.mkdir(parents=True, exist_ok=True)

    # Normalize apps to a list of strings
    app_list = [str(a) for a in apps if str(a).strip()]

    # Heuristic: if users are included/running, make others depend on "users"
    # so foreign keys like created_by load correctly.
    requires_users = include_users or ("users" in app_list)

    # Write fixtures for each selected app
    exported_any = False
    for app_label in app_list:
        data_json = _dump_app_fixture(app_label)
        (fixtures_dir / f"{app_label}.json").write_text(data_json, encoding="utf-8")
        exported_any = True

    # Always add a stub so discover_seedpacks() finds this even if no data
    (pack_dir / "seed_stub.py").write_text(
        "from django.core.management.base import BaseCommand\n\n"
        "class Command(BaseCommand):\n"
        "    help = 'Seed stub'\n\n"
        "    def handle(self, *args, **options):\n"
        "        self.stdout.write('Seed stub ran (no-op).')\n",
        encoding="utf-8",
    )

    # Generate seed_<app>.py loaders
    for app_label in app_list:
        requires_line = ""
        if requires_users and app_label != "users":
            requires_line = "REQUIRES = ['users']\n\n"
        loader = (
            "from pathlib import Path\n"
            "from django.core.management import call_command\n"
            "from django.core.management.base import BaseCommand\n\n"
            f"{requires_line}"
            "class Command(BaseCommand):\n"
            f"    help = 'Load fixtures for app: {app_label}'\n\n"
            "    def handle(self, *args, **options):\n"
            "        here = Path(__file__).resolve().parent\n"
            f"        fixture = here / 'fixtures' / '{app_label}.json'\n"
            "        if not fixture.exists():\n"
            "            self.stdout.write(self.style.WARNING(f'No fixture found: {fixture}'))\n"
            "            return\n"
            "        self.stdout.write(f'Loading {fixture.name}...')\n"
            "        call_command('loaddata', str(fixture))\n"
            "        self.stdout.write(self.style.SUCCESS('OK'))\n"
        )
        (pack_dir / f"seed_{app_label}.py").write_text(loader, encoding="utf-8")

    # Manifest
    manifest = {
        "name": name,
        "slug": slug,
        "apps": app_list,
        "include_users": bool(include_users),
        "include_media": bool(include_media),
        "exported_by": exported_by,
        "exported_at": datetime.utcnow().isoformat() + "Z",
        "schema": 1,
        "notes": "Fixtures contain PKs; run order matters when there are FKs. "
                 "Seed files will loaddata per-app. If users included, other apps depend on users.",
        "exported_any_data": bool(exported_any),
    }
    (pack_dir / "seedpack.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # Zip the pack directory
    zip_path = SEEDPACKS_DIR / f"{slug}.zip"
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in pack_dir.rglob("*"):
            zf.write(p, arcname=f"{slug}/{p.relative_to(pack_dir)}")

    print(f"[export_seedpack] wrote dir={pack_dir} zip={zip_path}")
    return {"slug": slug, "dir": str(pack_dir), "zip": str(zip_path)}

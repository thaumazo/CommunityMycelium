from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.management import call_command
from django.conf import settings
from django.http import FileResponse, Http404
from django.urls import reverse
from pathlib import Path
import shutil
import zipfile
import json
from datetime import datetime

from apps.core.seedpacks.loader import discover_seedpacks
from apps.core.seedpacks.exporter import export_seedpack, SEEDPACKS_DIR
from .forms_seedpacks import SeedpackExportForm, SeedpackUploadForm


def _zip_info_for(slug: str):
    z = SEEDPACKS_DIR / f"{slug}.zip"
    if z.exists():
        try:
            mtime = datetime.fromtimestamp(z.stat().st_mtime)
        except Exception:
            mtime = None
        return True, mtime
    return False, None


@staff_member_required
def seedpack_list(request):
    """
    Show available seedpacks with zip status (exists/mtime) for UI.
    Assumes discover_seedpacks() yields items with 'name' (or .name).
    """
    raw = discover_seedpacks()
    packs = []
    for item in raw:
        name = item["name"] if isinstance(item, dict) else getattr(item, "name", str(item))
        zip_exists, zip_mtime = _zip_info_for(name)
        packs.append(
            {
                "name": name,
                "zip_exists": zip_exists,
                "zip_mtime": zip_mtime,
            }
        )
    return render(request, "core/seedpacks/list.html", {"packs": packs})


@staff_member_required
def seedpack_export(request):
    """
    Render/export a seedpack. Supports `?prefill=<slug>` to prefill the name.
    """
    if request.method == "POST":
        form = SeedpackExportForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            apps = form.cleaned_data["apps"]
            result = export_seedpack(
                name,
                apps,
                exported_by=request.user.email or request.user.username,
                include_users=form.cleaned_data.get("include_users", False),
                include_media=form.cleaned_data.get("include_media", False),
            )
            messages.success(request, f"Exported seedpack '{result['slug']}'.")
            # Show a success page with a download link via our view
            zip_url = reverse("core:seedpack_download_zip", args=[result["slug"]])
            return render(
                request,
                "core/seedpacks/export_done.html",
                {
                    "slug": result["slug"],
                    "zip_url": zip_url,
                    "zip_abspath": result["zip"],  # optional: handy to show absolute path
                },
            )            
    else:
        initial = {}
        prefill = request.GET.get("prefill")
        if prefill:
            initial["name"] = prefill
        form = SeedpackExportForm(initial=initial)

    return render(request, "core/seedpacks/export.html", {"form": form})


@staff_member_required
def seedpack_upload(request):
    """
    Upload a zipped seedpack and place it under SEEDPACKS_DIR/<slug>/...
    Handles zips with or without a top-level folder.
    Optionally run it immediately if form.activate_now is checked.
    """
    if request.method == "POST":
        form = SeedpackUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.cleaned_data["file"]  # or ["zip_file"] if you chose that name
            if not upload.name.lower().endswith(".zip"):
                messages.error(request, "Please upload a .zip file.")
                return redirect("core:seedpack_upload")

            SEEDPACKS_DIR.mkdir(parents=True, exist_ok=True)

            tmp_zip = SEEDPACKS_DIR / ("_upload_" + upload.name)
            tmp_dir = SEEDPACKS_DIR / ("_unzipped_" + upload.name.replace(".zip", ""))
            try:
                # save uploaded zip
                with open(tmp_zip, "wb") as f:
                    for chunk in upload.chunks():
                        f.write(chunk)

                # unzip into a temp dir
                if tmp_dir.exists():
                    shutil.rmtree(tmp_dir)
                tmp_dir.mkdir(parents=True, exist_ok=True)

                with zipfile.ZipFile(tmp_zip, "r") as z:
                    z.extractall(tmp_dir)

                # find manifest (either at tmp_dir root or within a single top-level folder)
                def find_manifest(base: Path) -> Path | None:
                    cand = base / "seedpack.json"
                    if cand.exists():
                        return cand
                    # if a single subfolder, check there
                    entries = [p for p in base.iterdir() if p.is_dir()]
                    if len(entries) == 1:
                        cand2 = entries[0] / "seedpack.json"
                        if cand2.exists():
                            return cand2
                    return None

                manifest_path = find_manifest(tmp_dir)
                if not manifest_path:
                    messages.error(request, "Invalid seedpack: seedpack.json not found.")
                    return redirect("core:seedpack_upload")

                # read slug
                with open(manifest_path, "r", encoding="utf-8") as mf:
                    manifest = json.load(mf)
                slug = manifest.get("slug")
                if not slug:
                    messages.error(request, "Invalid seedpack: manifest missing 'slug'.")
                    return redirect("core:seedpack_upload")

                dest = SEEDPACKS_DIR / slug
                if dest.exists():
                    shutil.rmtree(dest)
                dest.mkdir(parents=True, exist_ok=True)

                # Decide what to move into dest:
                # - If manifest is at tmp_dir/seedpack.json -> move all of tmp_dir contents.
                # - If manifest is at tmp_dir/<top>/seedpack.json -> move that folder's contents.
                top_to_move = manifest_path.parent
                if top_to_move == tmp_dir:
                    # move all contents of tmp_dir into dest
                    for p in tmp_dir.iterdir():
                        # skip our temp artifacts if any
                        if p.name.startswith("_upload_") or p.name.startswith("_unzipped_"):
                            continue
                        shutil.move(str(p), dest / p.name)
                else:
                    # move only the top folder contents
                    for p in top_to_move.iterdir():
                        shutil.move(str(p), dest / p.name)

                messages.success(request, f"Seedpack '{slug}' uploaded.")
                if form.cleaned_data.get("activate_now"):
                    try:
                        call_command("run_seedpack", slug)
                        messages.success(request, f"Seedpack '{slug}' executed.")
                    except Exception as e:
                        messages.error(request, f"Upload OK, but run failed: {e}")

                return redirect("core:seedpack_list")

            finally:
                try:
                    tmp_zip.unlink(missing_ok=True)
                except Exception:
                    pass
                if tmp_dir.exists():
                    shutil.rmtree(tmp_dir, ignore_errors=True)
    else:
        form = SeedpackUploadForm()

    return render(request, "core/seedpacks/upload.html", {"form": form})

@staff_member_required
def seedpack_download_zip(request, slug):
    """
    Stream the zip file for a seedpack.
    """
    zip_path = SEEDPACKS_DIR / f"{slug}.zip"
    if not zip_path.exists():
        raise Http404("Zip not found. Re-export to create it.")
    return FileResponse(open(zip_path, "rb"), as_attachment=True, filename=f"{slug}.zip")

@staff_member_required
@require_POST
def seedpack_run(request, slug):
    """
    Execute a seedpack by slug. Expects POST (you already have a POST form in list.html).
    """
    try:
        call_command("run_seedpack", slug)
        messages.success(request, f"Seedpack '{slug}' ran successfully.")
    except Exception as e:
        messages.error(request, f"Error running seedpack '{slug}': {e}")
    return redirect("core:seedpack_list")
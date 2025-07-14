from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from apps.core.seedpacks.loader import discover_seedpacks
from django.core.management import call_command


@staff_member_required
def seedpack_list(request):
    packs = discover_seedpacks()
    return render(request, "core/seedpacks/list.html", {"packs": packs})


@staff_member_required
def seedpack_run(request, slug):
    if request.method == "GET":
        # Render confirmation prompt
        return render(request, "core/seedpacks/confirm_run.html", {"slug": slug})

    elif request.method == "POST":
        try:
            call_command("run_seedpack", slug)
            messages.success(request, f"Seedpack '{slug}' loaded successfully.")
        except Exception as e:
            messages.error(request, f"Error running seedpack: {e}")
        return redirect("core:seedpack_list")

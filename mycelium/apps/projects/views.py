from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from .models import Project
from .forms import ProjectForm
from django.core.exceptions import PermissionDenied
from apps.utils.dump import dump
from apps.utils.pagination import paginate_queryset


@login_required
def project_list_view(request):
    projects = get_permitted_objects(request.user, "view", Project)
    
    # Pagination using helper function
    projects_page, pagination_data = paginate_queryset(projects, request, per_page=10)
    
    return render(request, "projects/project_list.html", {
        "projects": projects_page,
        "pagination": pagination_data,
    })


@login_required
def project_detail_view(request, pk):
    project = get_permitted_object(request.user, "view", Project, pk)
    return render(request, "projects/project_detail.html", {"project": project})


@login_required
def project_create_view(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            form.save()  # This will save the project and m2m fields
            messages.success(request, "Project created successfully!")
            return redirect("project_list")
    else:
        form = ProjectForm()

    return render(
        request,
        "projects/project_form.html",
        {"form": form},
    )


@login_required
def project_edit_view(request, pk):
    project = get_permitted_object(request.user, "change", Project, pk)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Project updated successfully!")
            return redirect("project_detail", pk=project.pk)
    else:
        form = ProjectForm(instance=project)

    return render(
        request,
        "projects/project_form.html",
        {"form": form, "project": project},
    )


@login_required
def project_delete_view(request, pk):
    project = get_permitted_object(request.user, "delete", Project, pk)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project deleted successfully!")
        return redirect("project_list")

    return render(request, "projects/project_confirm_delete.html", {"project": project})

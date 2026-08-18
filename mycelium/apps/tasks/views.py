from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from .models import Task
from .forms import TaskForm
from django.core.exceptions import PermissionDenied
from apps.utils.pagination import paginate_queryset
from apps.utils.form_tokens import get_form_token, validate_form_token
from apps.utils.superuser_fields import attach_creator_field, apply_creator_field

@login_required
def task_list_view(request):
    tab_type = request.GET.get('tab', 'all')
    
    if tab_type == 'my':
        tasks = Task.objects.filter(assigned_to=request.user)
        active_tab = 'my'
    else:
        tasks = get_permitted_objects(request.user, "view", Task)
        active_tab = 'all'
    
    # Pagination using helper function
    tasks_page, pagination_data = paginate_queryset(tasks, request, per_page=10)
    
    return render(request, "tasks/task_list.html", {
        "tab_type": tab_type,
        "tasks": tasks_page,
        "pagination": pagination_data,
        "active_tab": active_tab,
    })

def task_detail_view(request, pk):
    task = get_permitted_object(request.user, "view", Task, pk)
    return render(request, "tasks/task_detail.html", {"task": task})


@login_required
def task_create_view(request):
    if not is_permitted(request.user, "add", "tasks.task"):
        raise PermissionDenied

    if request.method == "POST":
        if not validate_form_token(request, 'task_create'):
            messages.error(request, "This form has already been submitted. Please don't use the back button after submitting.")
            form = TaskForm()
            form_token = get_form_token(request, 'task_create')
            return render(request, "tasks/task_form.html", {"form": form, "form_token": form_token})
        
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, "Task created successfully!")
            return redirect("task_detail", pk=task.pk)
    else:
        form = TaskForm()

    form_token = get_form_token(request, 'task_create')
    return render(
        request,
        "tasks/task_form.html",
        {"form": form, "form_token": form_token},
    )


@login_required
def task_edit_view(request, pk):
    task = get_permitted_object(request.user, "change", Task, pk)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        attach_creator_field(form, request.user, task)
        if form.is_valid():
            form.save()
            apply_creator_field(form, request.user, task)
            messages.success(request, "Task updated successfully!")
            return redirect("task_detail", pk=task.pk)
    else:
        form = TaskForm(instance=task)
        attach_creator_field(form, request.user, task)

    return render(
        request,
        "tasks/task_form.html",
        {"form": form, "task": task},
    )


@login_required
def task_delete_view(request, pk):
    task = get_permitted_object(request.user, "delete", Task, pk)

    if request.method == "POST":
        task.delete()
        messages.success(request, "Task deleted successfully!")
        return redirect("task_list")

    return render(request, "tasks/task_confirm_delete.html", {"task": task})

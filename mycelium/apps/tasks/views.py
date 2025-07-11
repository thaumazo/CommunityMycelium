from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from .models import Task
from .forms import TaskForm
from django.core.exceptions import PermissionDenied


@login_required
def task_list_view(request):
    tasks = get_permitted_objects(request.user, "view", Task)
    
    # Pagination
    paginator = Paginator(tasks, 10)  # Show 10 tasks per page
    page = request.GET.get('page')
    
    try:
        tasks_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        tasks_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        tasks_page = paginator.page(paginator.num_pages)
    
    return render(request, "tasks/task_list.html", {
        "tasks": tasks_page,
        "page_obj": tasks_page,
        "paginator": paginator,
    })


@login_required
def task_detail_view(request, pk):
    task = get_permitted_object(request.user, "view", Task, pk)
    return render(request, "tasks/task_detail.html", {"task": task})


@login_required
def task_create_view(request):
    if not is_permitted(request.user, "add", "tasks.task"):
        raise PermissionDenied

    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, "Task created successfully!")
            return redirect("task_list")
    else:
        form = TaskForm()

    return render(
        request,
        "tasks/task_form.html",
        {"form": form},
    )


@login_required
def task_edit_view(request, pk):
    task = get_permitted_object(request.user, "change", Task, pk)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated successfully!")
            return redirect("task_detail", pk=task.pk)
    else:
        form = TaskForm(instance=task)

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

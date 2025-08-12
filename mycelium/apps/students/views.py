from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from .models import Student
from .forms import StudentForm
from django.core.exceptions import PermissionDenied
from apps.utils.dump import dump
from apps.utils.pagination import paginate_queryset


@login_required
def student_list_view(request):
    students = get_permitted_objects(request.user, "view", Student)
    
    # Pagination using helper function
    students_page, pagination_data = paginate_queryset(students, request, per_page=10)
    
    return render(request, "students/student_list.html", {
        "students": students_page,
        "pagination": pagination_data,
    })


@login_required
def student_detail_view(request, pk):
    student = get_permitted_object(request.user, "view", Student, pk)
    return render(request, "students/student_detail.html", {"student": student})


@login_required
def student_create_view(request):
    if not is_permitted(request.user, "add", "students.student"):
        raise PermissionDenied

    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.created_by = request.user
            student.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, "Student created successfully!")
            return redirect("student_list")
    else:
        form = StudentForm()

    return render(
        request,
        "students/student_form.html",
        {"form": form},
    )


@login_required
def student_edit_view(request, pk):
    student = get_permitted_object(request.user, "change", Student, pk)

    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Student updated successfully!")
            return redirect("student_detail", pk=student.pk)
    else:
        form = StudentForm(instance=student)

    return render(
        request,
        "students/student_form.html",
        {"form": form, "student": student},
    )


@login_required
def student_delete_view(request, pk):
    student = get_permitted_object(request.user, "delete", Student, pk)

    if request.method == "POST":
        student.delete()
        messages.success(request, "Student deleted successfully!")
        return redirect("student_list")

    return render(
        request, "students/student_confirm_delete.html", {"student": student}
    )

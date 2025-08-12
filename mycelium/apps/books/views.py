from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from .models import Book
from .forms import BookForm
from django.core.exceptions import PermissionDenied
from apps.utils.dump import dump
from apps.utils.pagination import paginate_queryset


@login_required
def book_list_view(request):
    books = get_permitted_objects(request.user, "view", Book)
    
    # Pagination using helper function
    books_page, pagination_data = paginate_queryset(books, request, per_page=10)
    
    return render(request, "books/book_list.html", {
        "books": books_page,
        "pagination": pagination_data,
    })


@login_required
def book_detail_view(request, pk):
    book = get_permitted_object(request.user, "view", Book, pk)
    return render(request, "books/book_detail.html", {"book": book})


@login_required
def book_create_view(request):
    if not is_permitted(request.user, "add", "books.book"):
        raise PermissionDenied

    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.created_by = request.user
            book.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, "Book created successfully!")
            return redirect("book_list")
    else:
        form = BookForm()

    return render(
        request,
        "books/book_form.html",
        {"form": form},
    )


@login_required
def book_edit_view(request, pk):
    book = get_permitted_object(request.user, "change", Book, pk)

    if request.method == "POST":
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, "Book updated successfully!")
            return redirect("book_detail", pk=book.pk)
    else:
        form = BookForm(instance=book)

    return render(
        request,
        "books/book_form.html",
        {"form": form, "book": book},
    )


@login_required
def book_delete_view(request, pk):
    book = get_permitted_object(request.user, "delete", Book, pk)

    if request.method == "POST":
        book.delete()
        messages.success(request, "Book deleted successfully!")
        return redirect("book_list")

    return render(
        request, "books/book_confirm_delete.html", {"book": book}
    )

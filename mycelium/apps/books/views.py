from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from .models import Book
from .forms import BookForm, ContentFormSet, ComprehensionWithinFormSet, ComprehensionAboutFormSet
from django.core.exceptions import PermissionDenied
from apps.utils.dump import dump
from apps.utils.pagination import paginate_queryset
from django.forms import inlineformset_factory
from .models import Content


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
        book = None
        if form.is_valid():
            book = form.save(commit=False)
            book.created_by = request.user
            book.save()
        content_formset = ContentFormSet(request.POST, instance=book)
        within_formset = ComprehensionWithinFormSet(request.POST, instance=book)
        about_formset = ComprehensionAboutFormSet(request.POST, instance=book)
        if form.is_valid() and content_formset.is_valid() and within_formset.is_valid() and about_formset.is_valid():
            form.save()
            content_formset.save()
            within_formset.save()
            about_formset.save()
            messages.success(request, "Book created successfully!")
            return redirect("book_list")
    else:
        form = BookForm()
        content_formset = ContentFormSet()
        within_formset = ComprehensionWithinFormSet()
        about_formset = ComprehensionAboutFormSet()

    return render(
        request,
        "books/book_form.html",
        {
            "form": form,
            "content_formset": content_formset,
            "within_formset": within_formset,
            "about_formset": about_formset,
        },
    )

@login_required
def book_edit_view(request, pk):
    book = get_permitted_object(request.user, "change", Book, pk)

    if request.method == "POST":
        form = BookForm(request.POST, instance=book)
        content_formset = ContentFormSet(request.POST, instance=book)
        within_formset = ComprehensionWithinFormSet(request.POST, instance=book)
        about_formset = ComprehensionAboutFormSet(request.POST, instance=book)
        if form.is_valid() and content_formset.is_valid() and within_formset.is_valid() and about_formset.is_valid():
            form.save()
            content_formset.save()
            within_formset.save()
            about_formset.save()
            messages.success(request, "Book updated successfully!")
            return redirect("book_detail", pk=book.pk)
    else:
        form = BookForm(instance=book)
        content_formset = ContentFormSet(instance=book)
        within_formset = ComprehensionWithinFormSet(instance=book)
        about_formset = ComprehensionAboutFormSet(instance=book)

    return render(
        request,
        "books/book_form.html",
        {
            "form": form,
            "book": book,
            "content_formset": content_formset,
            "within_formset": within_formset,
            "about_formset": about_formset,
        },
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

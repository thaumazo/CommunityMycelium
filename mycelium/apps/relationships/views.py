from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from .models import Relationship
from .forms import RelationshipForm
from django.core.exceptions import PermissionDenied
from apps.utils.dump import dump
from apps.utils.pagination import paginate_queryset


@login_required
def relationship_list_view(request):
    relationships = get_permitted_objects(request.user, "view", Relationship)
    
    # Pagination using helper function
    relationships_page, pagination_data = paginate_queryset(relationships, request, per_page=10)
    
    return render(request, "relationships/relationship_list.html", {
        "relationships": relationships_page,
        "pagination": pagination_data,
    })


@login_required
def relationship_detail_view(request, pk):
    relationship = get_permitted_object(request.user, "view", Relationship, pk)
    return render(request, "relationships/relationship_detail.html", {"relationship": relationship})


@login_required
def relationship_create_view(request):
    if not is_permitted(request.user, "add", "relationships.relationship"):
        raise PermissionDenied

    if request.method == "POST":
        form = RelationshipForm(request.POST)
        if form.is_valid():
            relationship = form.save(commit=False)
            relationship.created_by = request.user
            relationship.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, "Relationship created successfully!")
            return redirect("relationship_list")
    else:
        form = RelationshipForm()

    return render(
        request,
        "relationships/relationship_form.html",
        {"form": form},
    )


@login_required
def relationship_edit_view(request, pk):
    relationship = get_permitted_object(request.user, "change", Relationship, pk)

    if request.method == "POST":
        form = RelationshipForm(request.POST, instance=relationship)
        if form.is_valid():
            form.save()
            messages.success(request, "Relationship updated successfully!")
            return redirect("relationship_detail", pk=relationship.pk)
    else:
        form = RelationshipForm(instance=relationship)

    return render(
        request,
        "relationships/relationship_form.html",
        {"form": form, "relationship": relationship},
    )


@login_required
def relationship_delete_view(request, pk):
    relationship = get_permitted_object(request.user, "delete", Relationship, pk)

    if request.method == "POST":
        relationship.delete()
        messages.success(request, "Relationship deleted successfully!")
        return redirect("relationship_list")

    return render(request, "relationships/relationship_confirm_delete.html", {"relationship": relationship})

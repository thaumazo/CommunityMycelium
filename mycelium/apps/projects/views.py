from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.acl.utils import get_permitted_objects, get_permitted_object, is_permitted
from .models import Project, ProjectCapitalIn, ProjectCapitalOut
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
    from apps.stories.models import Story, StoryAttachment
    from django.contrib.contenttypes.models import ContentType
    from django.db.models import Q
    
    project = get_permitted_object(request.user, "view", Project, pk)
    
    # Get through model instances for capitals
    project_capitals_in = ProjectCapitalIn.objects.filter(project=project).select_related('capital')
    project_capitals_out = ProjectCapitalOut.objects.filter(project=project).select_related('capital')
    
    # Get stories attached to project capital relationships
    story_attachments = {}
    
    # Helper function to filter stories by visibility
    def get_visible_attachments(attachments):
        visible = []
        for attachment in attachments:
            story = attachment.story
            if request.user.is_authenticated:
                if (story.created_by == request.user or 
                    story.view_members or 
                    story.view_public or 
                    request.user.is_superuser):
                    visible.append(attachment)
            else:
                if story.view_public:
                    visible.append(attachment)
        return visible
    
    # Get stories for capitals in (attached to ProjectCapitalIn instances)
    for project_capital in project_capitals_in:
        ct = ContentType.objects.get_for_model(project_capital)
        attachments = StoryAttachment.objects.filter(
            content_type=ct,
            object_id=project_capital.id
        ).select_related('story', 'story__created_by')
        
        visible_stories = get_visible_attachments(attachments)
        if visible_stories:
            # Key by capital_in id for template
            story_attachments[f'capital_in_{project_capital.capital.id}'] = visible_stories
    
    # Get stories for capitals out (attached to ProjectCapitalOut instances)
    for project_capital in project_capitals_out:
        ct = ContentType.objects.get_for_model(project_capital)
        attachments = StoryAttachment.objects.filter(
            content_type=ct,
            object_id=project_capital.id
        ).select_related('story', 'story__created_by')
        
        visible_stories = get_visible_attachments(attachments)
        if visible_stories:
            # Key by capital_out id for template
            story_attachments[f'capital_out_{project_capital.capital.id}'] = visible_stories
    
    return render(request, "projects/project_detail.html", {
        "project": project,
        "story_attachments": story_attachments,
        "project_capitals_in": project_capitals_in,
        "project_capitals_out": project_capitals_out,
    })


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

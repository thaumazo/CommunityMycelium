from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from apps.relationships.models import RelationshipProposal

@login_required
def home_view(request):
    proposals = (
        RelationshipProposal.objects.filter(
            status=RelationshipProposal.Status.PENDING
        )
        .filter(
            Q(to_person=request.user)
            | Q(to_community__owners=request.user)
            | Q(to_community__admins=request.user)
            | Q(to_project__owners=request.user)
            | Q(to_project__admins=request.user)
        )
        .select_related(
            "initiator",
            "from_person",
            "from_community",
            "from_project",
            "to_person",
            "to_community",
            "to_project",
            "resolution",
            "relationship_type",
        )
        .distinct()
    )
    return render(request, "core/home.html", {"proposals": proposals})

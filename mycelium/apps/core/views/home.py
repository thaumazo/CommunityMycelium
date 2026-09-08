from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from apps.relationships.models import RelationshipProposal
from apps.commons.models import Commons, CommonsApplication, CommonsInvite
from apps.commons.utils import get_user_commons_queryset

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

    my_commons = get_user_commons_queryset(request.user).order_by("title").distinct()
    pending_commons_invites = CommonsInvite.objects.filter(
        invited_user=request.user, status=CommonsInvite.STATUS_PENDING
    ).select_related("commons", "invited_by")
    pending_commons_applications = CommonsApplication.objects.filter(
        commons__in=my_commons, status=CommonsApplication.STATUS_PENDING
    ).select_related("commons", "applicant")

    return render(request, "core/home.html", {
        "proposals": proposals,
        "my_commons": my_commons,
        "pending_commons_invites": pending_commons_invites,
        "pending_commons_applications": pending_commons_applications,
    })


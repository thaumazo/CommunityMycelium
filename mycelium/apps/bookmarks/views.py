from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from apps.acl.utils import is_permitted

from .models import Bookmark


@login_required
def bookmark_list_view(request):
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('content_type').order_by('-created_at')
    return render(request, 'bookmarks/bookmark_list.html', {
        'bookmarks': bookmarks,
    })


@login_required
def bookmark_toggle_view(request, app_label, model, object_pk):
    content_type = get_object_or_404(ContentType, app_label=app_label, model=model)
    target_object = get_object_or_404(content_type.model_class(), pk=object_pk)

    if not is_permitted(request.user, 'view', target_object):
        raise PermissionDenied

    bookmark, created = Bookmark.objects.get_or_create(
        user=request.user,
        content_type=content_type,
        object_id=target_object.pk,
    )

    if not created:
        bookmark.delete()
        messages.success(request, 'Removed from favourites.')
    else:
        messages.success(request, 'Added to favourites.')

    next_url = request.POST.get('next') or request.GET.get('next') or request.META.get('HTTP_REFERER')
    return redirect(next_url or '/')

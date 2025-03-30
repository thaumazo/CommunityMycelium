from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.users.urls")),  # This is causing the issue
    path("meetings/", include("apps.meetings.urls")),  # Add this line for web interface
    path("api/users/", include("apps.users.urls")),  # Existing users API
    path("api/orgs/", include("apps.orgs.urls")),
    path("api/teams/", include("apps.teams.urls")),
    path("api/projects/", include("apps.projects.urls")),
    path("api/meetings/", include("apps.meetings.urls")),
    path("api/tasks/", include("apps.tasks.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

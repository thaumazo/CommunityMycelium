from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.users.urls")),  # This is causing the issue
    path("api/users/", include("apps.users.urls")),  # Existing users API
    path("api/orgs/", include("apps.orgs.urls")),
    path("api/teams/", include("apps.teams.urls")),
    path("api/projects/", include("apps.projects.urls")),
    path("api/meetings/", include("apps.meetings.urls")),
    path("api/tasks/", include("apps.tasks.urls")),
]

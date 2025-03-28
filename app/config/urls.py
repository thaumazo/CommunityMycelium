from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("apps.users.urls")),
    path("api/orgs/", include("apps.orgs.urls")),
    path("api/teams/", include("apps.teams.urls")),
    path("api/projects/", include("apps.projects.urls")),
    path("api/meetings/", include("apps.meetings.urls")),
    path("api/tasks/", include("apps.tasks.urls")),
]

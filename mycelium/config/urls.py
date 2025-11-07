from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(("apps.pages.urls", "pages"), namespace="pages")),  # Serve home.md for root URL
    path("core/", include("apps.core.urls")),  # Core app handles other website pages
    path("users/", include("apps.users.urls")),  # User management routes
    path("students/", include("apps.students.urls")),  # User management routes
    path("books/", include("apps.books.urls")),  # User management routes
    path("reading_sessions/", include("apps.reading_sessions.urls")),
    path("meetings/", include("apps.meetings.urls")),
    path("communities/", include("apps.communities.urls")),
    path("projects/", include("apps.projects.urls")),
    path("hats/", include("apps.hats.urls")),
    path("agreements/", include("apps.agreements.urls")),
    path("tasks/", include("apps.tasks.urls")),
    path("media_uploads/", include("apps.media_uploads.urls")),
    path("acl/", include("apps.acl.urls")),  # Access Control List routes
    path("pages/", include("apps.pages.urls")),  # Pages app routes
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

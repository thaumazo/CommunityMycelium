from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    # API routes
    path("api/", include("apps.api.urls")),
    # Web routes
    path("", include(("apps.pages.urls", "pages"), namespace="pages")),  # Serve home.md for root URL
    path("core/", include("apps.core.urls")),  # Core app handles other website pages
    path("users/", include("apps.users.urls")),  # User management routes
    path("meetings/", include("apps.meetings.urls")),
    path("communities/", include("apps.communities.urls")),
    path("projects/", include("apps.projects.urls")),
    path("socialroles/", include("apps.socialroles.urls")),
    path("maladaptives/", include("apps.maladaptives.urls")),
    path("metacrisis_facets/", include("apps.metacrisis_facets.urls")),
    path("capitals/", include("apps.capitals.urls")),
    path("bioregions/", include("apps.bioregions.urls")),
    path("challenges/", include("apps.challenges.urls")),
    path("relationships/", include("apps.relationships.urls")),
    path("resolutions/", include("apps.resolutions.urls")),
    path("tasks/", include("apps.tasks.urls")),
    path("acl/", include("apps.acl.urls")),  # Access Control List routes
    path("pages/", include("apps.pages.urls")),  # Pages app routes
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

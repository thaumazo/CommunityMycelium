from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls")),  # Core app handles main website pages
    path("users/", include("apps.users.urls")),  # User management routes
    path("meetings/", include("apps.meetings.urls")),
    path("acl/", include("apps.acl.urls")),  # Access Control List routes
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

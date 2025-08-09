from django.urls import path
from apps.core.views import seedpack_ui
from apps.core.views.home import home_view  # ✅ correct import

app_name = "core"

urlpatterns = [
    path("", home_view, name="home"),  # whatever your home view import is
    path("seedpacks/", seedpack_ui.seedpack_list, name="seedpack_list"),
    path("seedpacks/export/", seedpack_ui.seedpack_export, name="seedpack_export"),
    path("seedpacks/upload/", seedpack_ui.seedpack_upload, name="seedpack_upload"),
    path("seedpacks/<slug:slug>/download/", seedpack_ui.seedpack_download_zip, name="seedpack_download_zip"),
    path("seedpacks/<slug:slug>/run/", seedpack_ui.seedpack_run, name="seedpack_run"),
]

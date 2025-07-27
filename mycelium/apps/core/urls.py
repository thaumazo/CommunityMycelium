from django.urls import path
from apps.core.views.home import home_view
from apps.core.views import seedpack_ui

app_name = "core"

urlpatterns = [
    path("seedpacks/", seedpack_ui.seedpack_list, name="seedpack_list"),
    path("seedpacks/<slug:slug>/run/", seedpack_ui.seedpack_run, name="seedpack_run"),
    path("", home_view, name="home"),
]

from django.urls import path
from .views import (
    bioregion_list_view,
    bioregion_create_view,
    bioregion_detail_view,
    bioregion_edit_view,
    bioregion_delete_view,
    bioregion_challenge_import_view,
    bioregion_tile_proxy_view,
)

urlpatterns = [
    path("", bioregion_list_view, name="bioregion_list"),
    path("create/", bioregion_create_view, name="bioregion_create"),
    path("<int:pk>/", bioregion_detail_view, name="bioregion_detail"),
    path("tiles/<str:provider>/<int:z>/<int:x>/<int:y>/", bioregion_tile_proxy_view, name="bioregion_tile_proxy"),
    path("tiles/<str:provider>/<int:z>/<int:x>/<int:y>.png", bioregion_tile_proxy_view),
    path("<int:pk>/import-challenges/", bioregion_challenge_import_view, name="bioregion_challenge_import"),
    path("<int:pk>/edit/", bioregion_edit_view, name="bioregion_edit"),
    path("<int:pk>/delete/", bioregion_delete_view, name="bioregion_delete"),
]

from django.urls import path
from .views import (
    metacrisis_facet_list_view,
    metacrisis_facet_create_view,
    metacrisis_facet_detail_view,
    metacrisis_facet_edit_view,
    metacrisis_facet_delete_view,
)

urlpatterns = [
    path("", metacrisis_facet_list_view, name="metacrisis_facet_list"),
    path("create/", metacrisis_facet_create_view, name="metacrisis_facet_create"),
    path("<int:pk>/", metacrisis_facet_detail_view, name="metacrisis_facet_detail"),
    path("<int:pk>/edit/", metacrisis_facet_edit_view, name="metacrisis_facet_edit"),
    path("<int:pk>/delete/", metacrisis_facet_delete_view, name="metacrisis_facet_delete"),
]

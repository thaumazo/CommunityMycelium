from django.urls import path

from . import views

urlpatterns = [
    path('', views.bookmark_list_view, name='bookmark_list'),
    path('toggle/<str:app_label>/<str:model>/<int:object_pk>/', views.bookmark_toggle_view, name='bookmark_toggle'),
]

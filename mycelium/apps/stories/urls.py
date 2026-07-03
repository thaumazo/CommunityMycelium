from django.urls import path
from . import views

urlpatterns = [
    path('', views.story_list_view, name='story_list'),
    path('attachment-options/', views.story_attachment_options_view, name='story_attachment_options'),
    path('<int:pk>/', views.story_detail_view, name='story_detail'),
    path('create/', views.story_create_view, name='story_create'),
    path('<int:pk>/edit/', views.story_edit_view, name='story_edit'),
    path('<int:pk>/delete/', views.story_delete_view, name='story_delete'),
    path('<int:story_pk>/add-media/', views.story_add_media_view, name='story_add_media'),
    path('media/<int:media_pk>/delete/', views.story_delete_media_view, name='story_delete_media'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('student/<int:student_id>/sessions/', views.student_reading_sessions, name='student_reading_sessions'),
    path('student/<int:student_id>/sessions/create/', views.reading_session_create, name='reading_session_create'),
    path('session/<int:session_id>/', views.reading_session_detail, name='reading_session_detail'),
    path('session/<int:session_id>/generate_transcript/', views.generate_transcript, name='generate_transcript'),
]
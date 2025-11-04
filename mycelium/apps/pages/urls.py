from django.urls import path
from .views import public_markdown_page

urlpatterns = [
    path('', public_markdown_page, {'slug': 'home'}, name='home'),  # Public home page
    path('pages/<slug:slug>/', public_markdown_page, name='page'),  # Pages under /pages/
]
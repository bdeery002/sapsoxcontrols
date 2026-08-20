from django.urls import path
from . import views

app_name = 'about'
urlpatterns = [
    path('', views.about, name='about'),
    path('author/', views.author_bio, name='author_bio'),  # Serves the author bio at /about/author/
]
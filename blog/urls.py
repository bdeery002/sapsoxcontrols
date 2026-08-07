from django.urls import path
from . import views

app_name = 'blog'

# blog/urls.py
urlpatterns = [
    path("", views.index, name="index"),
    path("search/", views.search, name="search"),
    
    # Matches <a href="{% url 'propose_edit' %}"> in your layout/sidebar
    path("propose/", views.propose_edit, name="propose_edit"),
    
    # Matches <a href="{% url 'propose_edit_with_title' title=title %}"> in entry.html
    path("propose/<str:title>/", views.propose_edit, name="propose_edit_with_title"),
    
    # Matches return redirect("entry", title=...) in views.py
    path("<str:title>/", views.entry, name="entry"),
]
from django.urls import path
from . import views

app_name = 'sox_controls'

urlpatterns = [
    path("", views.index, name="index"),
    path("load-workflow/<str:workflow_name>/", views.load_workflow, name="load_workflow"),
    path("filter/process/<str:process_slug>/", views.filter_by_process, name="filter_by_process"),
    path("filter/subprocess/<str:subprocess_slug>/", views.filter_by_subprocess, name="filter_by_subprocess"),
    path('<str:control_id>/', views.control_detail, name='control_detail'),
    path("process-narratives/<slug:slug>/",views.process_narrative,name="process_narrative"),
]



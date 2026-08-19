from django.urls import path
from . import views

app_name = 'itgc'

urlpatterns = [
    path('', views.index, name='index'),
    path('workflow/<str:workflow_name>/', views.load_workflow, name='load_workflow'),
    path('filter/layer/<str:layer_slug>/', views.filter_by_layer, name='filter_by_layer'),
    path('filter/category/<str:category_slug>/', views.filter_by_category, name='filter_by_category'),
    path('control/<str:control_id>/', views.control_detail, name='control_detail'),
    path('narratives/<slug:slug>/', views.itgc_narrative, name='itgc_narrative'),
]

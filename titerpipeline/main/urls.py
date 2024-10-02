from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('samples/', views.samples_by_experiment, name='samples_by_experiment'),
    path('/filtered-samples', views.filter_samples, name='filter_samples'),
    path('export-csv/', views.export_csv, name='export_csv'),
]
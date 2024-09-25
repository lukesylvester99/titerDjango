from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('samples/', views.samples_by_experiment, name='samples_by_experiment'),
    path('', views.filter_samples, name='filter_samples'),
]
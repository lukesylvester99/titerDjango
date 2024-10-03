from django.urls import path
from django.contrib.auth import views as auth_views  # Import LoginView from auth_views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='authenticate/login.html'), name='login'),
]

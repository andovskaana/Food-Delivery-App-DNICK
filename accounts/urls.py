"""
URL configuration for the accounts app.
"""
from django.urls import path  # type: ignore
from .views import RegisterView, LoginView, LogoutView, AdminDashboardView

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('admin/dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
]

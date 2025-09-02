"""
Views for the accounts app.

These views handle user registration, login, and logout. They make
use of Django's generic views where appropriate and customize the
templates to integrate with the rest of the site.
"""
from __future__ import annotations

from django.contrib.auth import login
from django.contrib.auth import views as auth_views  # type: ignore
from django.shortcuts import redirect
from django.urls import reverse_lazy  # type: ignore
from django.views.generic import FormView  # type: ignore

from .forms import UserRegistrationForm, LoginForm
from .models import User

from django.contrib.auth.mixins import LoginRequiredMixin  # type: ignore
from django.core.exceptions import PermissionDenied  # type: ignore
from django.views.generic import TemplateView  # type: ignore


class RegisterView(FormView):
    """
    Handle user registration. Upon successful registration, the user is
    automatically logged in and redirected to the home page.
    """
    template_name = 'accounts/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('home')

    def form_valid(self, form: UserRegistrationForm):  # type: ignore
        user: User = form.save(commit=False)
        # Set role directly from the form's cleaned_data
        user.role = form.cleaned_data.get('role', User.ROLE_CUSTOMER)
        user.save()
        # Automatically log the user in
        login(self.request, user)
        return redirect(self.get_success_url())


class LoginView(auth_views.LoginView):  # type: ignore
    """
    Display the login form and handle the login action.
    """
    form_class = LoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


class LogoutView(auth_views.LogoutView):  # type: ignore
    """
    Logout the current user and redirect to the home page.
    """
    next_page = reverse_lazy('home')


class AdminDashboardView(LoginRequiredMixin, TemplateView):
    """
    A simple dashboard for administrators. This view displays links to
    manage users, restaurants and products. Only users with the admin
    role or superusers may access this page.
    """
    template_name = 'accounts/admin_dashboard.html'

    def dispatch(self, request, *args, **kwargs):  # type: ignore[override]
        if not request.user.is_authenticated or not request.user.is_admin():
            raise PermissionDenied('You do not have permission to access the admin dashboard.')
        return super().dispatch(request, *args, **kwargs)

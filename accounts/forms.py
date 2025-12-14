"""
Forms for user registration and authentication.

These forms leverage Django's built-in `UserCreationForm` and
`AuthenticationForm` to provide a user-friendly interface for signing
up and logging in. The registration form exposes the `role` field so
users can select whether they're a customer or restaurant owner.
"""
from django import forms  # type: ignore
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm  # type: ignore
from .models import User


class UserRegistrationForm(UserCreationForm):
    """Extend Django's built-in user creation form to include roles."""

    role = forms.ChoiceField(
        choices=[(User.ROLE_CUSTOMER, 'Customer'), (User.ROLE_OWNER, 'Restaurant Owner')],
        required=True,
        help_text='Select your role on the platform.'
    )

    class Meta(UserCreationForm.Meta):  # type: ignore
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'role')

class LoginForm(AuthenticationForm):
    """Simple subclass of Django's authentication form to customize widgets."""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
    )
    password = forms.CharField(
        label='Password',
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
    )

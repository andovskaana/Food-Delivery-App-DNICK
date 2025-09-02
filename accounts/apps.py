"""
Configuration for the accounts app which manages user authentication and roles.
"""
from django.apps import AppConfig  # type: ignore


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'Accounts'

"""
Configuration for the payments app.
"""
from django.apps import AppConfig  # type: ignore


class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payments'
    verbose_name = 'Payments'

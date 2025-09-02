"""
Configuration for the orders app.
"""
from django.apps import AppConfig  # type: ignore


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'
    verbose_name = 'Orders'

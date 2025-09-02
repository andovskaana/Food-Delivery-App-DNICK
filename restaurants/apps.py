"""
Configuration for the restaurants app.
"""
from django.apps import AppConfig  # type: ignore


class RestaurantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'restaurants'
    verbose_name = 'Restaurants'

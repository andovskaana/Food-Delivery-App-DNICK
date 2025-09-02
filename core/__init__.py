"""
Core package for the food delivery Django project.

This module sets the default application configuration for the core
sub‑package. By specifying ``default_app_config``, Django will load
``CoreConfig`` from ``core.apps`` by default. The configuration
automatically seeds the database on startup when no restaurants are
present, making the application ready to use after initial migration.
"""

default_app_config = "core.apps.CoreConfig"

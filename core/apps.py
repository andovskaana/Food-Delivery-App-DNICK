"""
App configuration for the core module.

In addition to declaring the application name, this configuration hooks
into Django's startup process to ensure that sample data is available
without requiring explicit user action. When the application starts and
no restaurants exist in the database, the built‑in management command
``seed_data`` will be invoked automatically. This behaviour mirrors the
Java backend's ``DataInitializer`` and helps developers and testers
begin using the system immediately.

If you wish to disable automatic seeding (for example, in a production
environment), set the environment variable ``FOOD_DELIVERY_NO_AUTO_SEED``
to any non‑empty value. You can also run ``python manage.py seed_data``
manually at any time.
"""

from __future__ import annotations

import os
import logging

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self) -> None:
        """Run on startup. Perform automatic data seeding when appropriate."""
        # Do not import models or call database if seeding is disabled via env var
        if os.environ.get("FOOD_DELIVERY_NO_AUTO_SEED"):
            return
        # Only attempt seeding when running inside the main process
        # When using runserver, Django sets the RUN_MAIN flag on the second
        # fork of the autoreloader. We check this to avoid duplicating work.
        if os.environ.get("RUN_MAIN") == "true" or os.environ.get("WERKZEUG_RUN_MAIN"):
            try:
                from django.db import OperationalError
                from restaurants.models import Restaurant  # type: ignore
                # Only seed if there are no restaurants yet
                if not Restaurant.objects.exists():
                    from django.core.management import call_command
                    logging.getLogger(__name__).info("No restaurants found. Running seed_data...")
                    call_command("seed_data")
            except OperationalError:
                # Database might not be ready yet (e.g. during migrations)
                pass

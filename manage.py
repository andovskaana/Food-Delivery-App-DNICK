#!/usr/bin/env python
"""
This file provides command-line functionality for the Django project.
It sets the default settings module and delegates to Django's management
command-line utility. Although this project may not run in the current
environment due to missing Django dependencies, the code is structured
to work correctly when Django is available.
"""
import os
import sys


def main() -> None:
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    try:
        from django.core.management import execute_from_command_line  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Make sure it's installed and available on your PYTHONPATH environment variable. "
            "Did you forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
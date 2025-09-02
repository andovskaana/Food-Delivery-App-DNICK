"""
Models for the accounts app.

The `User` model extends Django's `AbstractUser` to include a role
attribute. Roles are used throughout the application to determine
access to different functionality (e.g. owners can manage their
restaurants, couriers see deliveries, etc.).
"""
from __future__ import annotations

from django.contrib.auth.models import AbstractUser  # type: ignore
from django.db import models  # type: ignore


class User(AbstractUser):
    """Custom user model with support for roles."""

    ROLE_CUSTOMER = 'customer'
    ROLE_COURIER = 'courier'
    ROLE_OWNER = 'owner'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES: list[tuple[str, str]] = [
        (ROLE_CUSTOMER, 'Customer'),
        (ROLE_COURIER, 'Courier'),
        (ROLE_OWNER, 'Owner'),
        (ROLE_ADMIN, 'Administrator'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_CUSTOMER,
        help_text='Designates the role of the user in the platform.'
    )

    def is_customer(self) -> bool:
        return self.role == self.ROLE_CUSTOMER

    def is_courier(self) -> bool:
        return self.role == self.ROLE_COURIER

    def is_owner(self) -> bool:
        return self.role == self.ROLE_OWNER

    def is_admin(self) -> bool:
        return self.role == self.ROLE_ADMIN or self.is_superuser

    def __str__(self) -> str:  # type: ignore[override]
        return self.username

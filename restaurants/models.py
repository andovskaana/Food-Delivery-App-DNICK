"""
Models for the restaurants app.

This module defines the core entities: `Restaurant`, `Product`, and
`Review`. Restaurants are owned by users with the owner role and can
contain multiple products. Customers can leave reviews on products.
"""
from __future__ import annotations

from django.conf import settings  # type: ignore
from django.db import models  # type: ignore


class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='restaurants/', blank=True, null=True)
    open_hours = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=100, blank=True)
    is_open = models.BooleanField(default=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_restaurants',
        help_text='The owner of this restaurant',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:  # type: ignore[override]
        return self.name


class Product(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='products',
        help_text='Restaurant that offers this product',
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:  # type: ignore[override]
        return f"{self.name} ({self.restaurant.name})"

    def increase_quantity(self, amount: int = 1) -> None:
        self.quantity = (self.quantity or 0) + amount
        self.save(update_fields=['quantity'])

    def decrease_quantity(self, amount: int = 1) -> None:
        if self.quantity < amount:
            raise ValueError('Insufficient quantity')
        self.quantity -= amount
        self.save(update_fields=['quantity'])


class Review(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='reviews'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews'
    )
    rating = models.PositiveIntegerField(default=5)
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')
        ordering = ['-created_at']

    def __str__(self) -> str:  # type: ignore[override]
        return f"Review of {self.product.name} by {self.user.username}"

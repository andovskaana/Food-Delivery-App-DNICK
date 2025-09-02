"""
Models for the payments app.

Defines the `Payment` model which records payment attempts for orders.
The payment provider and status fields mirror those in the original
project. Amount and currency are stored redundantly to capture the
price at time of payment.
"""
from __future__ import annotations

from django.db import models  # type: ignore
from django.conf import settings  # type: ignore
from orders.models import Order


class Payment(models.Model):
    PROVIDER_STRIPE = 'stripe'
    PROVIDER_CHOICES = [
        (PROVIDER_STRIPE, 'Stripe'),
    ]

    STATUS_REQUIRES_ACTION = 'requires_action'
    STATUS_AUTHORIZED = 'authorized'
    STATUS_CAPTURED = 'captured'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_REQUIRES_ACTION, 'Requires Action'),
        (STATUS_AUTHORIZED, 'Authorized'),
        (STATUS_CAPTURED, 'Captured'),
        (STATUS_FAILED, 'Failed'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default=PROVIDER_STRIPE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_REQUIRES_ACTION)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='usd')
    provider_intent_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:  # type: ignore[override]
        return f"Payment #{self.pk} for Order #{self.order_id}" if self.pk else 'Unsaved Payment'

"""
Models for the orders app.

Defines the `Order` and `OrderItem` models which capture a user's
purchase from a restaurant. Orders belong to a single restaurant and
comprise one or more order items. Totals are stored redundantly to
speed up rendering and to decouple them from changes in product
prices after an order is placed.
"""
from __future__ import annotations

from decimal import Decimal
from django.conf import settings  # type: ignore
from django.db import models  # type: ignore
from restaurants.models import Restaurant, Product


class Order(models.Model):
    """
    Represents a purchase from a restaurant. Orders start in the ``pending`` state
    when created from the cart. Once a payment is successfully captured the
    status transitions to ``confirmed`` and the order becomes available for
    assignment by a courier. When a courier picks up an order the status is
    updated to ``picked_up`` and, finally, to ``delivered`` once the order has
    reached the customer. Canceled orders remain in the ``canceled`` state.
    """
    STATUS_PLACED = "placed" # moja promena
    STATUS_ACCEPTED = "accepted"
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_PICKED_UP = 'picked_up'
    STATUS_CANCELED = 'canceled'
    STATUS_DELIVERED = 'delivered'

    STATUS_CHOICES: list[tuple[str, str]] = [
        (STATUS_PLACED, "Placed"), # moja promena
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_PICKED_UP, 'Picked up'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_CANCELED, 'Canceled'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        help_text='The customer who placed the order',
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='orders',
        help_text='Restaurant that will fulfil the order',
    )
    courier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='deliveries',
        null=True,
        blank=True,
        help_text='Courier assigned to deliver the order',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PLACED, #moja promena
        help_text='Current status of the order',
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Sum of line totals before delivery fees',
    )
    delivery_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Delivery fee applied to the order',
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Grand total including fees',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:  # type: ignore[override]
        return f"Order #{self.pk} for {self.user.username}"

    def recalc_totals(self) -> None:
        subtotal = Decimal('0.00')
        for item in self.items.all():
            subtotal += item.line_total
        self.subtotal = subtotal
        # Delivery fee could be computed based on restaurant or distance; for simplicity set to 0
        self.delivery_fee = Decimal('0.00')
        self.total = subtotal + self.delivery_fee
        self.save(update_fields=['subtotal', 'delivery_fee', 'total'])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('order', 'product')

    @property
    def line_total(self) -> Decimal:
        return self.price_at_time * self.quantity

    def __str__(self) -> str:  # type: ignore[override]
        return f"{self.quantity} × {self.product.name}"

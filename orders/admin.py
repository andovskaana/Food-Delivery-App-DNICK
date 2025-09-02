"""
Admin configuration for orders and order items.
"""
from django.contrib import admin  # type: ignore
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price_at_time', 'line_total')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'restaurant', 'status', 'total', 'created_at')
    list_filter = ('status', 'restaurant')
    inlines = [OrderItemInline]

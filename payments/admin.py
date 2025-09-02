"""
Admin registration for the Payment model.
"""
from django.contrib import admin  # type: ignore
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'amount', 'currency', 'provider', 'status', 'created_at')
    list_filter = ('provider', 'status')
    search_fields = ('order__id', 'provider_intent_id')

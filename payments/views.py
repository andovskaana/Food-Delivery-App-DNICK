"""
Views for the payments app.

These API-like views mirror the functionality of the original backend by
creating Stripe PaymentIntents, simulating payment success and failure,
and retrieving payment details. They return JSON responses that can
easily be consumed by JavaScript running in templates or by a
front-end application.
"""
from __future__ import annotations

import uuid
from decimal import Decimal

from django.conf import settings  # type: ignore
from django.contrib.auth.mixins import LoginRequiredMixin  # type: ignore
from django.http import (
    JsonResponse,
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotAllowed,
)  # type: ignore
from django.shortcuts import get_object_or_404  # type: ignore
from django.utils.decorators import method_decorator  # type: ignore
from django.views import View  # type: ignore
from django.views.decorators.http import require_POST  # type: ignore

from orders.models import Order
from .models import Payment

try:
    import stripe  # type: ignore
except ImportError:
    stripe = None  # type: ignore


def _status_val(model_cls, fallback: str) -> str:
    """Return a status constant if it exists on the model, otherwise fallback."""
    return getattr(model_cls, f"STATUS_{fallback.upper()}", fallback)


class PaymentIntentView(LoginRequiredMixin, View):
    """
    Create or update a PaymentIntent for a given order. Returns JSON with
    the Payment ID, client secret (if available) and other details.
    """

    def post(self, request: HttpRequest, order_id: int) -> HttpResponse:
        order = get_object_or_404(Order, pk=order_id, user=request.user)

        # Get or create the payment linked to this order
        payment, _ = Payment.objects.get_or_create(order=order)

        # Sync amount/currency to the order
        # Adjust 'order.total' if your Order uses a different field name
        payment.amount = Decimal(order.total)
        payment.currency = 'usd'

        client_secret = None
        # Use Stripe when available and API key configured
        if stripe is not None and getattr(settings, 'STRIPE_SECRET_KEY', None):
            try:
                stripe.api_key = settings.STRIPE_SECRET_KEY
                amount_cents = int(payment.amount * 100)

                if not payment.provider_intent_id:
                    intent = stripe.PaymentIntent.create(
                        amount=amount_cents,
                        currency=payment.currency,
                        automatic_payment_methods={'enabled': True},
                        metadata={'order_id': order.id, 'user_id': request.user.id},
                    )
                    payment.provider_intent_id = intent.get('id')

                if payment.provider_intent_id:
                    intent = stripe.PaymentIntent.retrieve(payment.provider_intent_id)
                    client_secret = intent.client_secret
            except Exception:
                # Keep app usable even if Stripe errors out; fall back to fake id
                if not payment.provider_intent_id:
                    payment.provider_intent_id = f"pi_{uuid.uuid4().hex}"
        else:
            # Stripe not installed/configured: fall back to fake intent id
            if not payment.provider_intent_id:
                payment.provider_intent_id = f"pi_{uuid.uuid4().hex}"

        # Move payment into "requires action" state; UI will confirm via Stripe or simulate
        payment.status = _status_val(Payment, "requires_action")
        payment.save()

        return JsonResponse({
            'id': payment.id,
            'client_secret': client_secret,
            'provider': getattr(payment, "provider", "stripe"),
            'status': payment.status,
        })


class PaymentGetView(LoginRequiredMixin, View):
    """Return current payment details as JSON."""

    def get(self, request: HttpRequest, payment_id: int) -> HttpResponse:
        payment = get_object_or_404(Payment, pk=payment_id, order__user=request.user)
        return JsonResponse({
            "id": payment.id,
            "order_id": payment.order_id,
            "amount": str(payment.amount),
            "currency": payment.currency,
            "status": payment.status,
            "provider_intent_id": payment.provider_intent_id,
        })


@method_decorator(require_POST, name="post")
class PaymentSimulateSuccessView(LoginRequiredMixin, View):
    """Dev helper: mark payment as succeeded (used when Stripe isn’t configured)."""

    def post(self, request: HttpRequest, payment_id: int) -> HttpResponse:
        payment = get_object_or_404(Payment, pk=payment_id, order__user=request.user)
        payment.status = _status_val(Payment, "succeeded")
        payment.save()
        return JsonResponse({"ok": True, "status": payment.status})


@method_decorator(require_POST, name="post")
class PaymentSimulateFailureView(LoginRequiredMixin, View):
    """Dev helper: mark payment as failed."""

    def post(self, request: HttpRequest, payment_id: int) -> HttpResponse:
        payment = get_object_or_404(Payment, pk=payment_id, order__user=request.user)
        payment.status = _status_val(Payment, "failed")
        payment.save()
        return JsonResponse({"ok": True, "status": payment.status})

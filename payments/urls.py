"""
URL configuration for the payments app.

These endpoints return JSON responses intended for consumption by
JavaScript (AJAX) clients. They are not designed for direct access
via the browser.
"""
from django.urls import path  # type: ignore
from .views import PaymentIntentView, PaymentGetView, PaymentSimulateSuccessView, PaymentSimulateFailureView

app_name = 'payments'

urlpatterns = [
    path('<int:order_id>/intent/', PaymentIntentView.as_view(), name='create_intent'),
    path('<int:payment_id>/', PaymentGetView.as_view(), name='get'),
    path('<int:payment_id>/simulate-success/', PaymentSimulateSuccessView.as_view(), name='simulate_success'),
    path('<int:payment_id>/simulate-failure/', PaymentSimulateFailureView.as_view(), name='simulate_failure'),
]

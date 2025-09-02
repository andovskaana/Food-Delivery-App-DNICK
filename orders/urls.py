"""
URL configuration for the orders app.
"""
from django.urls import path  # type: ignore
from .views import (
    AddToCartView,
    CartView,
    CheckoutView,
    CheckoutPaymentView,
    MyOrdersView,
    OwnerOrdersView,
    CourierOrdersView,
    CourierDashboardView,
    CourierAssignOrderView,
    CourierCompleteOrderView,
    OrderConfirmView,
)

app_name = 'orders'

urlpatterns = [
    path('add/<int:product_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/', CartView.as_view(), name='cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('checkout/<int:order_id>/pay/', CheckoutPaymentView.as_view(), name='checkout_pay'),
    path('my/', MyOrdersView.as_view(), name='my_orders'),
    path('owner/', OwnerOrdersView.as_view(), name='owner_orders'),
    # Dashboard and actions for couriers
    path('courier/', CourierOrdersView.as_view(), name='courier_orders'),
    path('courier/dashboard/', CourierDashboardView.as_view(), name='courier_dashboard'),
    path('courier/assign/<int:order_id>/', CourierAssignOrderView.as_view(), name='courier_assign'),
    path('courier/complete/<int:order_id>/', CourierCompleteOrderView.as_view(), name='courier_complete'),
    path('<int:order_id>/confirm/', OrderConfirmView.as_view(), name='order_confirm'),
]

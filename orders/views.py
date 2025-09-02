"""
Views for the orders app.

This module contains a small shopping-cart implementation stored in
session data. Users can add products to their cart, review the cart,
create orders and proceed to checkout. Payment integration is handled
in the payments app via API endpoints.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Dict

from django.contrib import messages  # type: ignore
from django.contrib.auth.mixins import LoginRequiredMixin  # type: ignore
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse  # type: ignore
from django.shortcuts import get_object_or_404, redirect, render  # type: ignore
from django.urls import reverse, reverse_lazy  # type: ignore
from django.views import View  # type: ignore

from django.core.exceptions import PermissionDenied  # type: ignore

from restaurants.models import Product, Restaurant
from .models import Order, OrderItem

# Typing imports
from typing import List


def _get_cart(session: Dict[str, int]) -> Dict[str, int]:
    """Return the cart dictionary from the session or an empty dict."""
    return session.setdefault('cart', {})


class AddToCartView(LoginRequiredMixin, View):
    """Add a product to the shopping cart. Accessible only to customers."""

    def get(self, request: HttpRequest, product_id: int) -> HttpResponse:
        product = get_object_or_404(Product, pk=product_id, is_available=True)
        cart: Dict[str, int] = _get_cart(request.session)
        product_key = str(product_id)
        cart[product_key] = cart.get(product_key, 0) + 1
        request.session.modified = True
        messages.success(request, f"Added {product.name} to your cart.")
        # Redirect back to the product's restaurant page
        return redirect('restaurants:detail', pk=product.restaurant_id)


class CartView(LoginRequiredMixin, View):
    """Display the current cart contents and allow updates or checkout."""

    template_name = 'orders/cart.html'

    def get(self, request: HttpRequest) -> HttpResponse:
        cart = _get_cart(request.session)
        items = []
        subtotal = Decimal('0.00')
        for product_id_str, quantity in cart.items():
            product = get_object_or_404(Product, pk=int(product_id_str))
            line_total = product.price * quantity
            items.append({'product': product, 'quantity': quantity, 'line_total': line_total})
            subtotal += line_total
        context = {
            'items': items,
            'subtotal': subtotal,
        }
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Update quantities or remove items based on submitted form data.
        Expect fields named `quantity_<product_id>` for each product.
        """
        cart = _get_cart(request.session)
        updated_cart: Dict[str, int] = {}
        for key in list(cart.keys()):
            field_name = f"quantity_{key}"
            qty_str = request.POST.get(field_name)
            if qty_str is not None:
                try:
                    qty = int(qty_str)
                except ValueError:
                    qty = cart.get(key, 1)
                if qty > 0:
                    updated_cart[key] = qty
        request.session['cart'] = updated_cart
        request.session.modified = True
        messages.success(request, 'Cart updated.')
        return redirect('orders:cart')


class CheckoutView(LoginRequiredMixin, View):
    """
    Create an order from the cart and redirect to the payment page.
    This view only handles the POST operation; on GET it displays a summary.
    """
    template_name = 'orders/checkout.html'

    def get(self, request: HttpRequest) -> HttpResponse:
        # Show summary of items in cart; if no items, redirect to cart
        cart = _get_cart(request.session)
        if not cart:
            messages.info(request, 'Your cart is empty.')
            return redirect('orders:cart')
        items = []
        subtotal = Decimal('0.00')
        restaurant: Restaurant | None = None
        for product_id_str, quantity in cart.items():
            product = get_object_or_404(Product, pk=int(product_id_str))
            if restaurant is None:
                restaurant = product.restaurant
            elif restaurant != product.restaurant:
                # In this simple implementation we enforce that the cart only contains items from the same restaurant
                messages.error(request, 'All items in the cart must be from the same restaurant.')
                return redirect('orders:cart')
            line_total = product.price * quantity
            items.append({'product': product, 'quantity': quantity, 'line_total': line_total})
            subtotal += line_total
        context = {
            'items': items,
            'subtotal': subtotal,
        }
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest) -> HttpResponse:
        cart = _get_cart(request.session)
        if not cart:
            messages.info(request, 'Your cart is empty.')
            return redirect('orders:cart')
        # Determine restaurant and ensure all items belong to same restaurant
        first_product: Product | None = None
        for product_id_str in cart.keys():
            product = get_object_or_404(Product, pk=int(product_id_str))
            if first_product is None:
                first_product = product
            elif first_product.restaurant != product.restaurant:
                messages.error(request, 'All items in the cart must be from the same restaurant to place an order.')
                return redirect('orders:cart')
        assert first_product is not None
        order = Order.objects.create(
            user=request.user,
            restaurant=first_product.restaurant,
            status=Order.STATUS_PENDING,
        )
        # Create OrderItems
        for product_id_str, quantity in cart.items():
            product = get_object_or_404(Product, pk=int(product_id_str))
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price_at_time=product.price,
            )
        # Recalculate totals
        order.recalc_totals()
        # Clear cart
        request.session['cart'] = {}
        request.session.modified = True
        # Redirect to payment start page
        return redirect('orders:checkout_pay', order_id=order.pk)


class CheckoutPaymentView(LoginRequiredMixin, View):
    """
    Show a payment page for a given order. The page will attempt to
    create a PaymentIntent via the payments API and render a Stripe
    payment form. If Stripe integration fails, fall back to simulated
    success and failure buttons.
    """
    template_name = 'orders/checkout.html'

    def get(self, request: HttpRequest, order_id: int) -> HttpResponse:
        order = get_object_or_404(Order, pk=order_id, user=request.user)
        # Build a cart-like structure from order items
        items = []
        for item in order.items.select_related('product').all():
            items.append({
                'product': item.product,
                'quantity': item.quantity,
                'line_total': item.line_total,
            })
        context = {
            'order': order,
            'items': items,
        }
        return render(request, self.template_name, context)


class MyOrdersView(LoginRequiredMixin, View):
    """List the authenticated user's orders."""
    template_name = 'orders/order_list.html'

    def get(self, request: HttpRequest) -> HttpResponse:
        orders = Order.objects.filter(user=request.user).select_related('restaurant')
        return render(request, self.template_name, {'orders': orders})


class OwnerOrdersView(LoginRequiredMixin, View):
    """List orders that belong to restaurants owned by the current user."""
    template_name = 'orders/order_list.html'

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated or not request.user.is_owner():
            raise PermissionDenied('You do not have access to owner orders.')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest) -> HttpResponse:
        orders = Order.objects.filter(restaurant__owner=request.user).select_related('user', 'restaurant')
        return render(request, self.template_name, {'orders': orders, 'owner_mode': True})


class CourierOrdersView(LoginRequiredMixin, View):
    """List orders for courier assignment (confirmed but not delivered)."""
    template_name = 'orders/order_list.html'

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated or not request.user.is_courier():
            raise PermissionDenied('You do not have access to courier orders.')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest) -> HttpResponse:
        orders = Order.objects.filter(status=Order.STATUS_CONFIRMED).select_related('user', 'restaurant')
        return render(request, self.template_name, {'orders': orders, 'courier_mode': True})


class CourierDashboardView(LoginRequiredMixin, View):
    """
    Dashboard for couriers. Shows three sections:
    1. Available orders (confirmed orders without a courier assigned)
    2. My active deliveries (orders assigned to the current user and not yet delivered)
    3. My delivered orders (orders delivered by the current courier)
    """
    template_name = 'orders/courier_dashboard.html'

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated or not request.user.is_courier():
            raise PermissionDenied('You do not have access to the courier dashboard.')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest) -> HttpResponse:
        available_orders = Order.objects.filter(
            status=Order.STATUS_CONFIRMED,
            courier__isnull=True,
        ).select_related('user', 'restaurant')
        my_active_orders = Order.objects.filter(
            courier=request.user,
            status__in=[Order.STATUS_CONFIRMED, Order.STATUS_PICKED_UP],
        ).select_related('user', 'restaurant')
        my_delivered_orders = Order.objects.filter(
            courier=request.user,
            status=Order.STATUS_DELIVERED,
        ).select_related('user', 'restaurant')
        context = {
            'available_orders': available_orders,
            'my_active_orders': my_active_orders,
            'my_delivered_orders': my_delivered_orders,
        }
        return render(request, self.template_name, context)


class CourierAssignOrderView(LoginRequiredMixin, View):
    """Assign a confirmed order to the current courier and mark it as picked up."""

    def post(self, request: HttpRequest, order_id: int) -> HttpResponse:
        if not request.user.is_courier():
            raise PermissionDenied('Only couriers can assign orders.')
        order = get_object_or_404(Order, pk=order_id)
        if order.status != Order.STATUS_CONFIRMED or order.courier_id is not None:
            return JsonResponse({'error': 'Order is not available for assignment.'}, status=400)
        order.courier = request.user
        order.status = Order.STATUS_PICKED_UP
        order.save(update_fields=['courier', 'status'])
        return JsonResponse({'id': order.id, 'status': order.status, 'courier': order.courier.username})


class CourierCompleteOrderView(LoginRequiredMixin, View):
    """Mark an order as delivered. Only the assigned courier may complete the order."""

    def post(self, request: HttpRequest, order_id: int) -> HttpResponse:
        order = get_object_or_404(Order, pk=order_id, courier=request.user)
        if order.status != Order.STATUS_PICKED_UP:
            return JsonResponse({'error': 'Order cannot be completed from its current status.'}, status=400)
        order.status = Order.STATUS_DELIVERED
        order.save(update_fields=['status'])
        return JsonResponse({'id': order.id, 'status': order.status})


class OrderConfirmView(LoginRequiredMixin, View):
    """Mark a pending order as confirmed. Returns JSON."""

    def post(self, request: HttpRequest, order_id: int) -> HttpResponse:
        order = get_object_or_404(Order, pk=order_id, user=request.user)
        order.status = Order.STATUS_CONFIRMED
        order.save(update_fields=['status'])
        return JsonResponse({'id': order.id, 'status': order.status})

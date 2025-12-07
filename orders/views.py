from __future__ import annotations

from decimal import Decimal
from typing import Dict

from django.conf import settings
from django.contrib import messages  # type: ignore
from django.contrib.auth.mixins import LoginRequiredMixin  # type: ignore
from django.core.exceptions import PermissionDenied  # type: ignore
from django.http import HttpRequest, HttpResponse, JsonResponse  # type: ignore
from django.shortcuts import get_object_or_404, render, redirect  # type: ignore
from django.views import View  # type: ignore

from restaurants.models import Product, Restaurant  # type: ignore
from .models import Order, OrderItem  # type: ignore


# -----------------------------------------------------------------------------
# Cart helpers
# -----------------------------------------------------------------------------

def _get_cart(session) -> Dict[str, int]:
    return session.setdefault('cart', {})


def _add_to_cart(session, product_id: int, quantity: int = 1) -> None:
    cart = _get_cart(session)
    cart[str(product_id)] = cart.get(str(product_id), 0) + quantity
    session.modified = True


def _remove_from_cart(session, product_id: int) -> None:
    cart = _get_cart(session)
    cart.pop(str(product_id), None)
    session.modified = True


# -----------------------------------------------------------------------------
# Views
# -----------------------------------------------------------------------------

class AddToCartView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, product_id: int) -> HttpResponse:
        _add_to_cart(request.session, product_id, 1)
        messages.success(request, 'Added to cart.')
        return redirect('orders:cart')

    # Allow GET so plain links work
    def get(self, request: HttpRequest, product_id: int) -> HttpResponse:
        return self.post(request, product_id)


class CartView(LoginRequiredMixin, View):
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
        return render(request, self.template_name, {'items': items, 'subtotal': subtotal})


class CheckoutView(LoginRequiredMixin, View):
    """
    Create an order from the cart and redirect to the payment page.
    On GET: show a summary using current product prices.
    On POST: create Order + OrderItems capturing price_at_time to satisfy NOT NULL.
    """
    template_name = 'orders/checkout.html'

    def get(self, request: HttpRequest) -> HttpResponse:
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
                messages.error(request, 'All items in the cart must be from the same restaurant.')
                return redirect('orders:cart')
            line_total = product.price * quantity
            items.append({'product': product, 'quantity': quantity, 'line_total': line_total})
            subtotal += line_total

        return render(
            request,
            self.template_name,
            {
                'items': items,
                'subtotal': subtotal,
                'STRIPE_PUBLIC_KEY': getattr(settings, 'STRIPE_PUBLIC_KEY', ''),
            },
        )

    def post(self, request: HttpRequest) -> HttpResponse:
        cart = _get_cart(request.session)
        if not cart:
            messages.info(request, 'Your cart is empty.')
            return redirect('orders:cart')

        # Validate and compute totals; capture price_at_time for each item
        line_items = []
        subtotal = Decimal('0.00')
        restaurant: Restaurant | None = None
        for product_id_str, quantity in cart.items():
            product = get_object_or_404(Product, pk=int(product_id_str))
            if restaurant is None:
                restaurant = product.restaurant
            elif restaurant != product.restaurant:
                messages.error(request, 'All items in the cart must be from the same restaurant.')
                return redirect('orders:cart')
            price_at_time = product.price  # capture snapshot for NOT NULL constraint
            line_total = price_at_time * quantity
            line_items.append((product, quantity, price_at_time, line_total))
            subtotal += line_total

        order = Order.objects.create(user=request.user, restaurant=restaurant, total=subtotal)
        for product, quantity, price_at_time, _ in line_items:
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price_at_time=price_at_time,  # <-- critical for the IntegrityError
            )

        # Clear cart
        request.session['cart'] = {}
        request.session.modified = True

        # Redirect to payment start page (Stripe page)
        return redirect('orders:checkout_pay', order_id=order.pk)


class CheckoutPaymentView(LoginRequiredMixin, View):
    """
    Show payment page for an existing order and pass STRIPE_PUBLIC_KEY to template.
    """
    template_name = 'orders/checkout.html'

    def get(self, request: HttpRequest, order_id: int) -> HttpResponse:
        order = get_object_or_404(Order, pk=order_id, user=request.user)

        # Build display list from OrderItems (use stored price_at_time)
        items = []
        for item in order.items.select_related('product').all():
            line_total = item.price_at_time * item.quantity
            items.append(
                {
                    'product': item.product,
                    'quantity': item.quantity,
                    'line_total': line_total,
                    'price_each': item.price_at_time,
                }
            )

        return render(
            request,
            self.template_name,
            {
                'order': order,
                'items': items,
                'subtotal': order.total,
                'STRIPE_PUBLIC_KEY': getattr(settings, 'STRIPE_PUBLIC_KEY', ''),
            },
        )


class MyOrdersView(LoginRequiredMixin, View):
    template_name = 'orders/order_list.html'

    def get(self, request: HttpRequest) -> HttpResponse:
        orders = Order.objects.filter(user=request.user).select_related('restaurant')
        return render(request, self.template_name, {'orders': orders})


class OwnerOrdersView(LoginRequiredMixin, View):
    template_name = 'orders/order_list.html'

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated:
            raise PermissionDenied('You do not have access to owner orders.')
        # if not request.user.is_authenticated or not request.user.is_owner():
        #     raise PermissionDenied('You do not have access to owner orders.')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest) -> HttpResponse:
        orders = (
            Order.objects.filter(restaurant__owner=request.user)
            .select_related('restaurant', 'user')
        )
        return render(request, self.template_name, {'orders': orders, 'owner_mode': True})


class CourierOrdersView(LoginRequiredMixin, View):
    template_name = 'orders/order_list.html'

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated or not request.user.is_courier():
            raise PermissionDenied('You do not have access to courier orders.')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest) -> HttpResponse:
        orders = Order.objects.filter(status=Order.STATUS_CONFIRMED).select_related('user', 'restaurant')
        return render(request, self.template_name, {'orders': orders, 'courier_mode': True})


class CourierDashboardView(LoginRequiredMixin, View):
    template_name = 'orders/courier_dashboard.html'

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated or not request.user.is_courier():
            raise PermissionDenied('You do not have access to the courier dashboard.')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest) -> HttpResponse:
        available_orders = (
            Order.objects.filter(status=Order.STATUS_CONFIRMED, courier__isnull=True)
            .select_related('user', 'restaurant')
        )
        my_active_orders = (
            Order.objects.filter(courier=request.user, status__in=[Order.STATUS_CONFIRMED, Order.STATUS_PICKED_UP])
            .select_related('user', 'restaurant')
        )
        my_delivered_orders = (
            Order.objects.filter(courier=request.user, status=Order.STATUS_DELIVERED)
            .select_related('user', 'restaurant')
        )
        return render(
            request,
            self.template_name,
            {
                'available_orders': available_orders,
                'my_active_orders': my_active_orders,
                'my_delivered_orders': my_delivered_orders,
            },
        )


def _is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


class CourierAssignOrderView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, order_id: int) -> HttpResponse:
        if not request.user.is_courier():
            raise PermissionDenied('Only couriers can assign orders.')
        order = get_object_or_404(Order, pk=order_id)
        if order.status != Order.STATUS_CONFIRMED or order.courier_id is not None:
            return JsonResponse({'error': 'Order is not available for assignment.'}, status=400)
        order.courier = request.user
        order.status = Order.STATUS_PICKED_UP
        order.save(update_fields=['courier', 'status'])
        if _is_ajax(request):
            return JsonResponse({'id': order.id, 'status': order.status, 'courier': order.courier.username})
        messages.success(request, f'Order #{order.id} assigned to you and marked as picked up.')
        return redirect('orders:courier_dashboard')


class CourierCompleteOrderView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, order_id: int) -> HttpResponse:
        order = get_object_or_404(Order, pk=order_id, courier=request.user)
        if order.status != Order.STATUS_PICKED_UP:
            return JsonResponse({'error': 'Order cannot be completed from its current status.'}, status=400)
        order.status = Order.STATUS_DELIVERED
        order.save(update_fields=['status'])
        if _is_ajax(request):
            return JsonResponse({'id': order.id, 'status': order.status})
        messages.success(request, f'Order #{order.id} marked as delivered.')
        return redirect('orders:courier_dashboard')


class OrderConfirmView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, order_id: int) -> HttpResponse:
        order = get_object_or_404(Order, pk=order_id)
        if not request.user.is_owner() or order.restaurant.owner != request.user:
            # raise PermissionDenied('Only the owner of the restaurant can confirm.')
            return redirect('orders:owner_orders')
        if order.status != Order.STATUS_PENDING:
            return JsonResponse({'error': 'Order is not pending.'}, status=400)
        order.status = Order.STATUS_CONFIRMED
        order.save(update_fields=['status'])
        messages.success(request, f'Order #{order.id} confirmed.')
        return redirect('orders:owner_orders')

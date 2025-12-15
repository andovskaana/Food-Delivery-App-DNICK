from __future__ import annotations

import hashlib
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


def _is_ajax(request: HttpRequest) -> bool:
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def _dummy_geocode_sk(address: str) -> tuple[float, float]:
    """
    Детерминистички "fake geocoding":
    - било кој текст (адреса) -> координати во рамки на Скопје
    - нема реален API, нема billing, 100% dummy за HCI проект
    - истата адреса секогаш дава исти координати
    """
    normalized = (address or "").strip().lower() or "skopje"
    h = hashlib.sha256(normalized.encode("utf-8")).digest()

    # 0..1
    x = int.from_bytes(h[0:2], "big") / 65535
    y = int.from_bytes(h[2:4], "big") / 65535

    # Приближна кутија околу Скопје (за demo изглед)
    lat_min, lat_max = 41.97, 42.03
    lng_min, lng_max = 21.38, 21.48

    lat = lat_min + (lat_max - lat_min) * x
    lng = lng_min + (lng_max - lng_min) * y
    return (round(lat, 6), round(lng, 6))


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

        # 1) Ја читаме адресата што корисникот ја внел во checkout form
        delivery_address = (request.POST.get('delivery_address') or '').strip() or 'Skopje'

        # 2) Ги пресметуваме ставките + subtotal и правиме проверка за еден ресторан
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

            price_at_time = product.price
            line_total = price_at_time * quantity
            line_items.append((product, quantity, price_at_time))
            subtotal += line_total

        if restaurant is None:
            messages.error(request, 'Unable to determine restaurant for this cart.')
            return redirect('orders:cart')

        # 3) Креираме нарачка и ја снимаме адресата во база
        order = Order.objects.create(
            user=request.user,
            restaurant=restaurant,
            status=Order.STATUS_PLACED,
            delivery_address=delivery_address,
            subtotal=subtotal,
            delivery_fee=Decimal('0.00'),
            total=subtotal,  # subtotal + delivery_fee (сега е 0)
        )

        # 4) Ги снимаме ставките со price_at_time (snapshot)
        for product, quantity, price_at_time in line_items:
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price_at_time=price_at_time,
            )

        # 5) Празниме cart
        request.session['cart'] = {}
        request.session.modified = True

        # 6) Одиме на payment чекор
        return redirect('orders:checkout_pay', order_id=order.pk)


class CheckoutPaymentView(LoginRequiredMixin, View):
    """
    Show payment page for an existing order and pass STRIPE_PUBLIC_KEY to template.
    """
    template_name = 'orders/checkout.html'

    def get(self, request: HttpRequest, order_id: int) -> HttpResponse:
        order = get_object_or_404(Order, pk=order_id, user=request.user)

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
            Order.objects.filter(
                status__in=[Order.STATUS_CONFIRMED],
                courier__isnull=True
            )
            .select_related('user', 'restaurant')
        )

        my_active_orders = (
            Order.objects.filter(
                courier=request.user,
                status__in=[Order.STATUS_ACCEPTED, Order.STATUS_PICKED_UP]
            )
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


class CourierAssignOrderView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, order_id: int) -> HttpResponse:
        if not request.user.is_courier():
            raise PermissionDenied('Only couriers can assign orders.')

        order = get_object_or_404(Order, pk=order_id)

        if order.status != Order.STATUS_CONFIRMED or order.courier_id is not None:
            return JsonResponse({'error': 'Order is not available for assignment.'}, status=400)

        order.courier = request.user
        order.status = Order.STATUS_ACCEPTED
        order.save(update_fields=['courier', 'status'])

        if _is_ajax(request):
            return JsonResponse({'id': order.id, 'status': order.status, 'courier': order.courier.username})

        messages.success(request, f'Order #{order.id} assigned to you and marked as accepted.')
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
    """
    Confirm order after payment (customer) OR by restaurant owner.
    - Allowed current status: PLACED
    - Result status: CONFIRMED
    """

    def post(self, request: HttpRequest, order_id: int) -> HttpResponse:
        order = get_object_or_404(Order, pk=order_id)

        is_owner = (
                hasattr(request.user, "is_owner")
                and request.user.is_owner()
                and order.restaurant.owner == request.user
        )
        is_customer = (order.user_id == request.user.id)

        if not (is_owner or is_customer):
            if _is_ajax(request):
                return JsonResponse({'error': 'Not allowed.'}, status=403)
            raise PermissionDenied('You do not have permission to confirm this order.')

        if order.status != Order.STATUS_PLACED:
            return JsonResponse({'error': 'Order cannot be confirmed in its current status.'}, status=400)

        order.status = Order.STATUS_CONFIRMED
        order.save(update_fields=['status'])

        if _is_ajax(request):
            return JsonResponse({'id': order.id, 'status': order.status})

        messages.success(request, f'Order #{order.id} confirmed.')
        return redirect('orders:owner_orders' if is_owner else 'orders:my_orders')


class CourierStartDeliveryView(LoginRequiredMixin, View):
    """
    Курирот ја означува нарачката дека е подигната од ресторан (ACCEPTED -> PICKED_UP).
    """

    def post(self, request: HttpRequest, order_id: int) -> HttpResponse:
        if not request.user.is_courier():
            raise PermissionDenied('Only couriers can start delivery.')

        order = get_object_or_404(Order, pk=order_id, courier=request.user)

        if order.status != Order.STATUS_ACCEPTED:
            return JsonResponse({'error': 'Order is not in an accepted state.'}, status=400)

        order.status = Order.STATUS_PICKED_UP
        order.save(update_fields=['status'])

        if _is_ajax(request):
            return JsonResponse({'id': order.id, 'status': order.status})

        messages.success(request, f'Order #{order.id} marked as picked up.')
        return redirect('orders:courier_dashboard')


class CourierOrderDetailView(LoginRequiredMixin, View):
    """
    Детален приказ за една нарачка за курирот:
    - ресторан
    - адреса за достава
    - ставка(и) од нарачката
    """
    template_name = "orders/courier_order_detail.html"

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated or not request.user.is_courier():
            raise PermissionDenied("You do not have access to courier order details.")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, order_id: int) -> HttpResponse:
        order = (
            Order.objects
            .select_related("restaurant", "user")
            .prefetch_related("items__product")
            .filter(pk=order_id)
            .first()
        )
        if not order:
            raise PermissionDenied("Order not found.")

        items = []
        for item in order.items.all():
            line_total = item.price_at_time * item.quantity
            items.append(
                {
                    "product": item.product,
                    "quantity": item.quantity,
                    "unit_price": item.price_at_time,
                    "line_total": line_total,
                }
            )

        context = {
            "order": order,
            "items": items,
            "total": order.total,
        }
        return render(request, self.template_name, context)


class OrderTrackingView(LoginRequiredMixin, View):
    """
    Страница каде корисникот ја следи нарачката.
    Логика на чекори и мапа:

    - PLACED        → чекор 1 (order placed)
    - CONFIRMED     → чекор 2 (confirmed / preparing)
    - ACCEPTED/PICKED_UP → чекор 3 (courier on the way)
    - DELIVERED     → чекор 4 (delivered)
    """
    template_name = 'orders/order_tracking.html'

    def get(self, request: HttpRequest, order_id: int) -> HttpResponse:
        order = get_object_or_404(Order, pk=order_id, user=request.user)
        status = order.status

        # ----- 1) Чекор за progress bar -----
        if status == Order.STATUS_PLACED:
            current_step = 1
        elif status == Order.STATUS_CONFIRMED:
            current_step = 2
        elif status in [Order.STATUS_ACCEPTED, Order.STATUS_PICKED_UP]:
            current_step = 3
        else:
            # DELIVERED или било што друго (PENDING/CANCELED) → последен чекор
            current_step = 4

        # ----- 2) Адреси и координати -----
        restaurant_address = (getattr(order.restaurant, "address", "") or "").strip() or "Skopje"
        delivery_address = (order.delivery_address or "").strip() or "Skopje"

        start_coords = _dummy_geocode_sk(restaurant_address)
        end_coords = _dummy_geocode_sk(delivery_address)

        # ----- 3) Дали воопшто да прикажеме мапа -----
        show_map = (
            order.courier_id is not None
            and status in [
                Order.STATUS_ACCEPTED,
                Order.STATUS_PICKED_UP,
                Order.STATUS_DELIVERED,
            ]
        )

        # ----- 4) Каде треба да стои скутерот (логика за front-end) -----
        if status in [Order.STATUS_PLACED, Order.STATUS_CONFIRMED]:
            courier_position = "restaurant"   # уште не е прифатена од курир
        elif status == Order.STATUS_ACCEPTED:
            courier_position = "restaurant"   # курир ја прифатил, но не тргнал
        elif status == Order.STATUS_PICKED_UP:
            courier_position = "in_transit"   # во движење
        elif status == Order.STATUS_DELIVERED:
            courier_position = "customer"     # стигнато кај клиентот
        else:
            courier_position = "restaurant"   # дефолт fallback

        # ----- 5) Дали да има анимација -----
        animate_courier = (status == Order.STATUS_PICKED_UP)

        context = {
            "order": order,
            "current_step": current_step,
            "from_label": order.restaurant.name,
            "to_label": order.user.get_full_name() or order.user.username,

            "restaurant_address": restaurant_address,
            "delivery_address": delivery_address,

            "show_map": show_map,
            "start_coords": start_coords,
            "end_coords": end_coords,
            "animate_courier": animate_courier,
            "courier_position": courier_position,
        }
        return render(request, self.template_name, context)

class OrderMarkDeliveredView(LoginRequiredMixin, View):
    """
    Mark an order as delivered when tracking animation finishes.
    This endpoint is called from the tracking page via AJAX/fetch.
    """

    def post(self, request: HttpRequest, order_id: int) -> HttpResponse:
        # Only the customer that owns the order may mark it as delivered
        order = get_object_or_404(Order, pk=order_id, user=request.user)

        # We expect the order to be in PICKED_UP state
        if order.status != Order.STATUS_PICKED_UP:
            return JsonResponse(
                {"error": "Order cannot be marked as delivered from its current status."},
                status=400,
            )

        order.status = Order.STATUS_DELIVERED
        order.save(update_fields=["status"])

        # For AJAX/fetch calls return JSON
        if _is_ajax(request):
            return JsonResponse({"ok": True, "status": order.status})

        # Fallback if someone calls it via normal POST
        messages.success(request, f"Order #{order.id} marked as delivered.")
        return redirect("orders:my_orders")


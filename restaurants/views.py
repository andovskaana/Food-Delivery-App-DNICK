from __future__ import annotations

from typing import Any
from django.db import models
from django.contrib.auth.mixins import LoginRequiredMixin  # type: ignore
from django.core.exceptions import PermissionDenied  # type: ignore
from django.shortcuts import get_object_or_404, redirect  # type: ignore
from django.urls import reverse_lazy  # type: ignore
from django.views import View  # type: ignore
from django.views.generic import ListView, DetailView, CreateView, UpdateView  # type: ignore
from django.contrib import messages  # type: ignore

from .models import Restaurant, Product
from .forms import RestaurantForm, ProductForm

from django.http import HttpResponse  # type: ignore


class HomeView(ListView):
    """Home page displaying a list of open restaurants with optional search."""
    model = Restaurant
    template_name = 'home.html'
    context_object_name = 'restaurants'

    def get_queryset(self):
        qs = Restaurant.objects.filter(is_open=True)
        term = self.request.GET.get("q", "").strip()
        if term:
            qs = qs.filter(
                models.Q(name__icontains=term) | models.Q(description__icontains=term)
            )
        return qs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        ctx['search_term'] = self.request.GET.get("q", "")
        return ctx


class OwnerRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not hasattr(request.user, 'role') or not request.user.is_owner():
            raise PermissionDenied("You do not have permission to access this page.")
        return super().dispatch(request, *args, **kwargs)


class RestaurantListView(ListView):
    model = Restaurant
    template_name = 'restaurants/restaurant_list.html'
    context_object_name = 'restaurants'


class RestaurantDetailView(DetailView):
    model = Restaurant
    template_name = 'restaurants/restaurant_detail.html'
    context_object_name = 'restaurant'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['products'] = self.object.products.filter(is_available=True)
        return context



class RestaurantCreateView(OwnerRequiredMixin, CreateView):
    model = Restaurant
    form_class = RestaurantForm
    template_name = 'restaurants/restaurant_form.html'
    success_url = reverse_lazy('restaurants:owner_restaurants')

    def form_valid(self, form: RestaurantForm):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RestaurantUpdateView(OwnerRequiredMixin, UpdateView):
    model = Restaurant
    form_class = RestaurantForm
    template_name = 'restaurants/restaurant_form.html'
    success_url = reverse_lazy('restaurants:owner_restaurants')

    def get_queryset(self):
        return Restaurant.objects.filter(owner=self.request.user)


class ProductCreateView(OwnerRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'restaurants/product_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.restaurant = get_object_or_404(Restaurant, pk=kwargs['restaurant_pk'], owner=request.user)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: ProductForm):
        form.instance.restaurant = self.restaurant
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse_lazy('restaurants:owner_restaurants')


class ProductUpdateView(OwnerRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'restaurants/product_form.html'

    def get_queryset(self):
        return Product.objects.filter(restaurant__owner=self.request.user)

    def get_success_url(self) -> str:
        return reverse_lazy('restaurants:owner_restaurants')


class OwnerRestaurantProductsView(OwnerRequiredMixin, ListView):
    model = Product
    template_name = 'restaurants/owner_product_list.html'
    context_object_name = 'products'

    def dispatch(self, request, *args, **kwargs):
        self.restaurant = get_object_or_404(Restaurant, pk=kwargs['restaurant_pk'], owner=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Product.objects.filter(restaurant=self.restaurant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['restaurant'] = self.restaurant
        return context


class ProductDeleteView(OwnerRequiredMixin, View):
    def post(self, request, pk: int) -> HttpResponse:
        # Наоѓаме продукт кој му припаѓа на тековниот owner
        product = get_object_or_404(
            Product,
            pk=pk,
            restaurant__owner=request.user
        )

        # Го бришеме продуктот
        product.delete()

        # Порака за успешно бришење
        messages.success(request, 'Product deleted.')

        # Го враќаме owner-от на My Restaurants (owner_restaurant_list.html)
        return redirect('restaurants:owner_restaurants')

class OwnerRestaurantListView(LoginRequiredMixin, ListView):
    model = Restaurant
    template_name = 'restaurants/owner_restaurant_list.html'
    context_object_name = 'restaurants'

    def get_queryset(self):
        # Сите ресторани на тековниот owner + нивните products
        return (
            Restaurant.objects
            .filter(owner=self.request.user)
            .prefetch_related('products')
        )

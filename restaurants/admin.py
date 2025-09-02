"""
Admin registration for restaurants, products and reviews.
"""
from django.contrib import admin  # type: ignore
from .models import Restaurant, Product, Review


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'category', 'is_open')
    list_filter = ('category', 'is_open')
    search_fields = ('name', 'owner__username')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'price', 'quantity', 'is_available')
    list_filter = ('restaurant', 'is_available')
    search_fields = ('name', 'restaurant__name')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('product__name', 'user__username')

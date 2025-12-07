from django.urls import path
from .views import (
    RestaurantListView, RestaurantDetailView,
    OwnerRestaurantListView, RestaurantCreateView, RestaurantUpdateView,
    OwnerRestaurantProductsView, ProductCreateView, ProductUpdateView, ProductDeleteView,
)

app_name = 'restaurants'

urlpatterns = [
    path('', RestaurantListView.as_view(), name='list'),
    path('<int:pk>/', RestaurantDetailView.as_view(), name='detail'),

    path('owner/create/', RestaurantCreateView.as_view(), name='create'),
    path('owner/<int:pk>/edit/', RestaurantUpdateView.as_view(), name='edit'),

    path('owner/<int:restaurant_pk>/products/', OwnerRestaurantProductsView.as_view(),
         name='owner_restaurant_products'),
    path('owner/<int:restaurant_pk>/products/create/', ProductCreateView.as_view(), name='product_create'),
    path('owner/products/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_edit'),
    path('owner/products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    path('owner/restaurants/', OwnerRestaurantListView.as_view(), name='owner_restaurants'),

]

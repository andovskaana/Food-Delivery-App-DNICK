"""
Forms for the restaurants app.

These forms are used by restaurant owners to manage their restaurants
and products. They automatically apply Bootstrap CSS classes to fields
for consistent styling across the application.
"""
from django import forms  # type: ignore
from .models import Restaurant, Product


class BaseBootstrapForm(forms.ModelForm):
    """Base form class that applies Bootstrap classes to all fields."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.setdefault('class', 'form-control')


class RestaurantForm(BaseBootstrapForm):
    class Meta:
        model = Restaurant
        exclude = ('owner', 'created_at', 'updated_at')


class ProductForm(BaseBootstrapForm):
    class Meta:
        model = Product
        exclude = ('restaurant', 'created_at', 'updated_at')

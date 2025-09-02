"""
Management command to seed the database with a starter dataset.

This command populates the application with a set of users, restaurants and
products mirroring the sample data from the provided Java backend. It is
idempotent: running the command multiple times will not create duplicate
records. User accounts are created with easily remembered passwords to
facilitate testing. If you wish to change these credentials in a production
setting, update the values below.

Usage::

    python manage.py seed_data

The command will create the following users:

* **admin** – administrator (username ``admin``, password ``admin``)
* **customer** – regular customer (username ``customer``, password ``customer``)
* **courier** – delivery courier (username ``courier``, password ``courier``)
* **owner** – restaurant owner (username ``owner``, password ``owner``)

It will also create ten restaurants, each with two products. The owner of
every restaurant is the ``owner`` user. Open hours are set to ``09:00–22:00``
and all restaurants are marked as open. Product quantities and prices are
copied from the Java sample. You can modify these values as needed.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import User
from restaurants.models import Restaurant, Product


class Command(BaseCommand):
    help = "Seed the database with initial data (users, restaurants, products)"

    def handle(self, *args, **options) -> None:
        """Entrypoint for the management command."""
        UserModel = get_user_model()
        # Create or update users
        admin, created = UserModel.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@email.com",
                "role": User.ROLE_ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin.set_password("admin")
            admin.save()
            self.stdout.write(self.style.SUCCESS("Created admin user."))

        customer, created = UserModel.objects.get_or_create(
            username="customer",
            defaults={
                "email": "customer@email.com",
                "role": User.ROLE_CUSTOMER,
            },
        )
        if created:
            customer.set_password("customer")
            customer.save()
            self.stdout.write(self.style.SUCCESS("Created customer user."))

        courier, created = UserModel.objects.get_or_create(
            username="courier",
            defaults={
                "email": "courier@email.com",
                "role": User.ROLE_COURIER,
            },
        )
        if created:
            courier.set_password("courier")
            courier.save()
            self.stdout.write(self.style.SUCCESS("Created courier user."))

        owner, created = UserModel.objects.get_or_create(
            username="owner",
            defaults={
                "email": "owner@email.com",
                "role": User.ROLE_OWNER,
            },
        )
        if created:
            owner.set_password("owner")
            owner.save()
            self.stdout.write(self.style.SUCCESS("Created owner user."))

        # Restaurant and product definitions replicating the Java initializer
        data = [
            (
                "The Green Garden",
                "A vegetarian and vegan-friendly restaurant offering fresh, organic meals and locally-sourced produce.",
                [
                    ("Vegan Buddha Bowl", "A bowl of quinoa, chickpeas, veggies, and tahini.", 9.99, 50),
                    ("Avocado Toast", "Whole grain toast topped with smashed avocado and microgreens.", 6.99, 40),
                ],
            ),
            (
                "Sushi World",
                "Authentic Japanese cuisine specializing in sushi, sashimi, and creative rolls made by expert chefs.",
                [
                    ("California Roll", "Crab, avocado, and cucumber rolled in seaweed and rice.", 8.50, 100),
                    ("Salmon Sashimi", "Fresh sliced salmon served with soy and wasabi.", 12.00, 70),
                ],
            ),
            (
                "Pasta Palace",
                "A cozy Italian spot known for its handmade pasta, rich sauces, and rustic charm.",
                [
                    ("Spaghetti Carbonara", "Classic pasta with pancetta, egg, and parmesan.", 11.99, 60),
                    ("Lasagna", "Layers of pasta, beef ragu, and creamy béchamel.", 13.50, 45),
                ],
            ),
            (
                "Spice Symphony",
                "An Indian restaurant offering a symphony of spices with classic curries, tandoori specialties, and biryani.",
                [
                    ("Chicken Tikka Masala", "Tender chicken in creamy spiced tomato sauce.", 10.99, 80),
                    ("Vegetable Biryani", "Fragrant rice with mixed vegetables and spices.", 9.50, 70),
                ],
            ),
            (
                "Burger Barn",
                "Casual American dining with gourmet burgers, loaded fries, and thick milkshakes.",
                [
                    ("Classic Cheeseburger", "Beef patty with cheddar, lettuce, tomato, and pickles.", 9.99, 120),
                    ("Bacon BBQ Burger", "Burger with crispy bacon, BBQ sauce, and onion rings.", 11.50, 90),
                ],
            ),
            (
                "Taco Fiesta",
                "A vibrant Mexican eatery serving tacos, burritos, and enchiladas with bold flavors and fresh ingredients.",
                [
                    ("Chicken Tacos", "Soft tacos with grilled chicken, salsa, and cheese.", 7.99, 100),
                    ("Beef Burrito", "Flour tortilla stuffed with seasoned beef, beans, and rice.", 9.25, 80),
                ],
            ),
            (
                "Dragon Wok",
                "Traditional Chinese food with modern twists, offering dim sum, stir-fries, and noodle products.",
                [
                    ("Kung Pao Chicken", "Spicy stir-fry with chicken, peanuts, and veggies.", 10.50, 60),
                    ("Vegetable Spring Rolls", "Crispy rolls filled with mixed vegetables.", 5.50, 150),
                ],
            ),
            (
                "Mediterranean",
                "Fine Mediterranean dining with products inspired by Greek, Turkish, and Lebanese cuisines.",
                [
                    ("Grilled Lamb Kebabs", "Tender lamb skewers with tzatziki sauce.", 14.00, 50),
                    ("Greek Salad", "Salad with feta, olives, cucumber, and tomatoes.", 7.00, 80),
                ],
            ),
            (
                "Ocean's Catch",
                "A seafood grill specializing in fresh catches, grilled platters, and seafood pasta.",
                [
                    ("Grilled Salmon", "Fresh salmon fillet with lemon butter sauce.", 16.99, 40),
                    ("Shrimp Alfredo", "Pasta with creamy Alfredo sauce and shrimp.", 15.50, 55),
                ],
            ),
            (
                "Sweet Tooth Bakery",
                "A delightful bakery and café with a wide selection of cakes, pastries, and artisan coffee.",
                [
                    ("Chocolate Cake", "Rich chocolate cake with ganache frosting.", 5.00, 90),
                    ("Blueberry Muffin", "Moist muffin packed with fresh blueberries.", 3.50, 120),
                ],
            ),
        ]

        created_any = False
        for name, description, products in data:
            restaurant, rest_created = Restaurant.objects.get_or_create(
                name=name,
                defaults={
                    "description": description,
                    "owner": owner,
                    "is_open": True,
                    "open_hours": "09:00–22:00",
                },
            )
            if rest_created:
                created_any = True
                self.stdout.write(self.style.SUCCESS(f"Created restaurant: {name}"))
            # Create products for the restaurant
            for prod_name, prod_desc, price, qty in products:
                product, prod_created = Product.objects.get_or_create(
                    restaurant=restaurant,
                    name=prod_name,
                    defaults={
                        "description": prod_desc,
                        "price": price,
                        "quantity": qty,
                        "is_available": True,
                    },
                )
                if prod_created:
                    created_any = True
                    self.stdout.write(self.style.SUCCESS(f"  Added product: {prod_name}"))

        if not created_any:
            self.stdout.write(self.style.WARNING("No new data created; seed data already present."))

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")
django.setup()

from alx_backend_graphql_crm.crm.models import Customer, Product

def run():
    # Seed Customers
    customers = [
        {"name": "Alice", "email": "alice@example.com", "phone": "+1234567890"},
        {"name": "Bob", "email": "bob@example.com", "phone": "123-456-7890"},
        {"name": "Carol", "email": "carol@example.com"}
    ]
    for c in customers:
        Customer.objects.get_or_create(**c)

    # Seed Products
    products = [
        {"name": "Laptop", "price": 999.99, "stock": 10},
        {"name": "Phone", "price": 499.99, "stock": 25},
        {"name": "Headphones", "price": 79.99, "stock": 50},
    ]
    for p in products:
        Product.objects.get_or_create(**p)

    print("✅ Database seeded successfully!")

if __name__ == "__main__":
    run()

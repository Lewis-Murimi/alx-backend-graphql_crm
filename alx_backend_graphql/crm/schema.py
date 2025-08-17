import re
import graphene
from graphene_django import DjangoObjectType
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Customer, Product, Order


# ------------------ GraphQL Types ------------------
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")


# ------------------ Mutations ------------------

# 1. CreateCustomer
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    customer = graphene.Field(CustomerType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

    def mutate(self, info, name, email, phone=None):
        errors = []

        # Email uniqueness
        if Customer.objects.filter(email=email).exists():
            errors.append("Email already exists")

        # Phone format validation
        if phone and not re.match(r"^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$", phone):
            errors.append("Invalid phone format. Use +1234567890 or 123-456-7890")

        if errors:
            return CreateCustomer(customer=None, message="Customer creation failed", errors=errors)

        customer = Customer(name=name, email=email, phone=phone)
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully!", errors=None)


# 2. BulkCreateCustomers
class BulkCreateCustomers(graphene.Mutation):
    class CustomerInput(graphene.InputObjectType):
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @transaction.atomic
    def mutate(self, info, input):
        created_customers = []
        errors = []

        for data in input:
            try:
                if Customer.objects.filter(email=data.email).exists():
                    raise ValidationError(f"Email already exists: {data.email}")

                if data.phone and not re.match(r"^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$", data.phone):
                    raise ValidationError(f"Invalid phone format: {data.phone}")

                customer = Customer.objects.create(
                    name=data.name,
                    email=data.email,
                    phone=data.phone
                )
                created_customers.append(customer)

            except Exception as e:
                errors.append(str(e))

        return BulkCreateCustomers(customers=created_customers, errors=errors)


# 3. CreateProduct
class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(required=False)

    product = graphene.Field(ProductType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, name, price, stock=0):
        errors = []

        if price <= 0:
            errors.append("Price must be positive")
        if stock < 0:
            errors.append("Stock cannot be negative")

        if errors:
            return CreateProduct(product=None, errors=errors)

        product = Product(name=name, price=price, stock=stock)
        product.save()
        return CreateProduct(product=product, errors=None)


# 4. CreateOrder
class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)

    order = graphene.Field(OrderType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, customer_id, product_ids):
        errors = []

        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            errors.append("Invalid customer ID")
            return CreateOrder(order=None, errors=errors)

        if not product_ids:
            errors.append("At least one product must be selected")
            return CreateOrder(order=None, errors=errors)

        products = Product.objects.filter(pk__in=product_ids)
        if len(products) != len(product_ids):
            errors.append("One or more product IDs are invalid")
            return CreateOrder(order=None, errors=errors)

        order = Order(customer=customer)
        order.save()
        order.products.set(products)
        order.total_amount = order.calculate_total()
        order.save()

        return CreateOrder(order=order, errors=None)


# ------------------ Schema Entry Point ------------------
class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(root, info):
        return Customer.objects.all()

    def resolve_products(root, info):
        return Product.objects.all()

    def resolve_orders(root, info):
        return Order.objects.all()


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.utils import timezone
from crm.models import Customer, Product, Order
from crm.models import Product
from .filters import CustomerFilter, ProductFilter, OrderFilter


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        filterset_class = CustomerFilter
        interfaces = (graphene.relay.Node,)


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        filterset_class = ProductFilter
        interfaces = (graphene.relay.Node,)


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        filterset_class = OrderFilter
        interfaces = (graphene.relay.Node,)


class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")

    all_customers = DjangoFilterConnectionField(CustomerType, order_by=graphene.List(of_type=graphene.String))
    all_products = DjangoFilterConnectionField(ProductType, order_by=graphene.List(of_type=graphene.String))
    all_orders = DjangoFilterConnectionField(OrderType, order_by=graphene.List(of_type=graphene.String))

    def resolve_all_customers(self, info, order_by=None, **kwargs):
        qs = Customer.objects.all()
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

    def resolve_all_products(self, info, order_by=None, **kwargs):
        qs = Product.objects.all()
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

    def resolve_all_orders(self, info, order_by=None, **kwargs):
        qs = Order.objects.all()
        if order_by:
            qs = qs.order_by(*order_by)
        return qs


# -------------------------
# Mutation for low-stock products
# -------------------------
class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass  # no arguments needed

    updated_products = graphene.List(ProductType)
    message = graphene.String()

    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated = []

        for product in low_stock_products:
            product.stock += 10
            product.save()
            updated.append(product)

        return UpdateLowStockProducts(
            updated_products=updated,
            message=f"{len(updated)} products updated on {timezone.now()}"
        )


class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)

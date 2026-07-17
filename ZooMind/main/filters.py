import django_filters
from .models import Pet, Product, Order


class PetFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    pet_type = django_filters.CharFilter(field_name="pet_type", lookup_expr="icontains")

    class Meta:
        model = Pet
        fields = ["name","pet_type"]


class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name="category", lookup_expr="icontains")
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    article = django_filters.CharFilter(field_name="article", lookup_expr="icontains")
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")

    class Meta:
        model = Product
        fields = ["name", "category", "article", "min_price", "max_price"]


class OrderFilter(django_filters.FilterSet):

    products = django_filters.NumberFilter(field_name="products__id", lookup_expr="exact")
    status = django_filters.CharFilter(field_name="status", lookup_expr="exact")
    created_after = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_befor = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Order
        fields = ["products", "status", "created_at"]
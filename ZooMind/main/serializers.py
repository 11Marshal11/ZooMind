from rest_framework import serializers
from .models import Pet, Product, Order

from django.db import transaction
from django.db.models import F

class PetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = [
            "id",
             "owner",
             "name",
             "pet_type"
            ]
        read_only_fields = ["owner"]

    def validate_name(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Имя питомца должно быть более двух символов")
        return value
    
    def validate_age(self, age):
        if age <= 0 or age >= 60:
            raise serializers.ValidationError("Возраст должен быть больше 0 и меньше 60")
        return age
        
    
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        
    def validate_price(self,value):
        if value <= 0:
            raise serializers.ValidationError("Цена товара должна быть больше 0")
        return value
    
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "owner",
            "products",
            "status",
            "created_at",
            "repeat_reminder_sent",
            "repeat_reminder_sent_at",
        ]
        read_only_fields = [
            "id",
            "owner",
            "status",
            "created_at",
            "repeat_reminder_sent",
            "repeat_reminder_sent_at",
        ]

    def validate(self, data):
        products = data.get("products")

        if not products:
            raise serializers.ValidationError(
                "В заказе должен быть хотя бы один товар"
            )

        for product in products:
            if product.stock_quantity <= 0:
                raise serializers.ValidationError(
                    f"Товара '{product.name}' нет на складе"
                )

        return data

    @transaction.atomic
    def create(self, validated_data):
        products = validated_data.pop("products")

        order = Order.objects.create(**validated_data)
        order.products.set(products)

        for product in products:
            updated = (
                Product.objects
                .filter(id=product.id, stock_quantity__gte=1)
                .update(stock_quantity=F("stock_quantity") - 1)
            )

            if updated == 0:
                raise serializers.ValidationError(
                    f"Товара '{product.name}' нет на складе"
                )

        return order
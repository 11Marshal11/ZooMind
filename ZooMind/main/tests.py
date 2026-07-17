
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from .models import Order
from .factories import OrderFactory, ProductFactory, UserFactory


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    CHANNEL_LAYERS={
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    },
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    },
)
class OrderAccessAndStockTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory(username="Daniel")
        self.other_user = UserFactory(username="OtherUser")

        self.product = ProductFactory(
            name="Вискас",
            article="WISKAS-001",
            category="food",
            pet_type="cat",
            price=12312,
            stock_quantity=5,
        )

    def test_authenticated_user_can_create_order(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
        "/api/orders/",
        {
            "products": [self.product.id],
        },
        format="json",
    )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
    )

        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Order.objects.first().owner, self.user)

    def test_stock_decreases_after_order_creation(self):
        self.client.force_authenticate(user=self.user)

        self.client.post(
            "/api/orders/",
        {
            "products": [self.product.id],
        },
        format="json",
    )

        self.product.refresh_from_db()

        self.assertEqual(self.product.stock_quantity, 4)


    def test_anonymous_user_cannot_create_order(self):
        response = self.client.post(
            "/api/orders/",
            {
                "products": [self.product.id],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Order.objects.count(), 0)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 5)

    def test_cannot_create_order_if_product_is_out_of_stock(self):
        self.client.force_authenticate(user=self.user)

        self.product.stock_quantity = 0
        self.product.save(update_fields=["stock_quantity"])

        response = self.client.post(
            "/api/orders/",
            {
                "products": [self.product.id],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.product.refresh_from_db()

        self.assertEqual(self.product.stock_quantity, 0)
        self.assertEqual(Order.objects.count(), 0)

    def test_user_sees_only_own_orders(self):
        user_order = OrderFactory(owner=self.user, products=[self.product])
        OrderFactory(owner=self.other_user, products=[self.product])

        self.client.force_authenticate(user=self.user)

        response = self.client.get("/api/orders/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]

        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], user_order.id)
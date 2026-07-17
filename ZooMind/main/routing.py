from django.urls import path

from .consumers import OrderNotificationConsumer


websocket_urlpatterns = [
    path("ws/orders/", OrderNotificationConsumer.as_asgi()),
    
]
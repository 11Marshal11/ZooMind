from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import PetViewSet, ProductViewSet, OrderViewSet, LoginTokenView

router = DefaultRouter()

router.register(r"pets", PetViewSet, basename="pets")
router.register(r"products", ProductViewSet, basename="products")
router.register(r"orders", OrderViewSet, basename="orders")

urlpatterns = [
    path("api/", include(router.urls)),

    path("api/token/", LoginTokenView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
 
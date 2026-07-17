from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Pet, Product, Order
from .serializers import PetSerializer, ProductSerializer, OrderSerializer
from .filters import PetFilter, ProductFilter, OrderFilter
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminOrReadOnly
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import action
from rest_framework.response import Response
from .services import RationRecommendationService
from django.db.models import Count
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

class PetViewSet(viewsets.ModelViewSet): 
    serializer_class = PetSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PetFilter
    search_fields = ["name", "pet_type"]
    ordering_fields = ["name", "pet_type"]

    def get_queryset(self):
        return (
            Pet.objects
            .filter(owner=self.request.user)
            .select_related("owner")
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        
    @action(detail=True, methods=["get"], url_path="recommendations")
    def recommendations(self, request, pk=None):
        pet = self.get_object()
        products = RationRecommendationService.get_recommendation_for_pet(pet)

        serializer = ProductSerializer(products, many=True)

        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "category", "article"]
    ordering_fields = ["name", "category", "article", "price"]

    @action(detail=False, methods=["get"], url_path="popular")
    @method_decorator(cache_page(60 * 5, key_prefix="popular_products"))
    def popular(self,request):
        products = (
            Product.objects
            .annotate(orders_count=Count("orders", distinct=True))
            .order_by("-orders_count", "price")[:10]
        )

        serializer = self.get_serializer(products, many=True)
        
        return Response(serializer.data)
    
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated] 

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OrderFilter
    search_fields = ["status", "owner__username", "products__name"]
    ordering_fields = ["status", "created_at"]

    def get_queryset(self):
        return (
            Order.objects
            .filter(owner=self.request.user)
            .select_related("owner")
            .prefetch_related("products")
            .order_by("-created_at")
    )
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
class LoginTokenView(TokenObtainPairView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"
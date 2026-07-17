from .models import Product, PetRecommendation
from django.db import transaction
from .ml_model import RationMLModel

class RationRecommendationService:
    @staticmethod
    def find_products_for_pet(pet, limit=5):
        products = Product.objects.filter(
            category=Product.FOOD,
            pet_type=pet.pet_type,
        ).order_by("price")

        return list(products[:limit])
        
        
    @classmethod
    def recalculate_for_pet(cls, pet, limit=5):
        products = cls.find_products_for_pet(pet, limit=limit)
        with transaction.atomic():
            PetRecommendation.objects.filter(pet=pet).delete()

            recommendations = [
                PetRecommendation(
                    pet=pet,
                    product=product,
                    score=RationMLModel.calculate_score(pet, product)
                )
            for product in products
            ]
            PetRecommendation.objects.bulk_create(recommendations)

        return products
    
    @classmethod
    def get_recommendation_for_pet(cls, pet, limit=5):
        saved_recommendations = (
            PetRecommendation.objects
            .filter(pet=pet)
            .select_related("product")
            .order_by("-score", "product__price")[:limit]
        )

        if saved_recommendations.exists():
            return [recommendation.product for recommendation in saved_recommendations]
        
        return cls.recalculate_for_pet(pet, limit=limit) 
        

    


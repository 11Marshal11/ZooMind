from django.core.cache import cache


class RationMLModel:
    is_loaded = False
    weights = {}

    @classmethod
    def load(cls):
        if cls.is_loaded:
            return

        cls.weights = {
            "same_pet_type": 70,
            "food_category": 30,
            "fallback": -10,
        }

        cls.is_loaded = True
        print("Ration ML model loaded")

    @classmethod
    def calculate_score(cls, pet, product):
        if not cls.is_loaded:
            cls.load()

        cache_key = f"ration_score:pet:{pet.id}:product:{product.id}"

        cached_score = cache.get(cache_key)

        if cached_score is not None:
            print(f"Score взят из кэша: {cache_key}")
            return cached_score

        score = 0

        if product.category == "food":
            score += cls.weights["food_category"]

        if product.pet_type == pet.pet_type:
            score += cls.weights["same_pet_type"]
        else:
            score += cls.weights["fallback"]

        cache.set(cache_key, score, timeout=60 * 30)

        print(f"Score рассчитан и сохранён в кэш: {cache_key}")

        return score
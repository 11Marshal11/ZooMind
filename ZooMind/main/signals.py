from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache



from .models import Pet, Product, Order
from .services import RationRecommendationService

from .tasks import send_repeat_purchase_reminder

@receiver(post_save, sender=Pet)
def recalculate_recommendations_after_pet_save(sender, instance, created, **kwargs):
    RationRecommendationService.recalculate_for_pet(instance)

@receiver(post_save, sender=Product)
def recalculate_recommdendations_after_product_save(sender, instance, created, **kwargs):
    if instance.category != Product.FOOD:
        return
    
    pets = Pet.objects.filter(pet_type=instance.pet_type)
    for pet in pets:
        RationRecommendationService.recalculate_for_pet(pet)

@receiver(post_save, sender= Order)
def send_order_created_notification(sender, instance, created, **kwargs):
    if not created:
        return
    
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        "warehouse_notifications",
        {
            "type": "order_created",
            "message": "Создан новый заказ",
            "order_id": instance.id,
            "status": instance.status,
            "owner": instance.owner.username if instance.owner else None,
        }
    )
    send_repeat_purchase_reminder.apply_async(
        args=[instance.id],
        countdown=30 * 24 * 60 * 60
    )

def clear_popular_products_cache():
    try:
        cache_storage = getattr(cache, "_cache", None)

        # Если используется Redis cache
        if hasattr(cache_storage, "get_client"):
            client = cache_storage.get_client(write=True)
            keys = client.keys("*popular_products*")

            if keys:
                client.delete(*keys)
                print(f"Кэш популярных товаров очищен. Удалено ключей: {len(keys)}")
            else:
                print("Кэш популярных товаров не найден")

            return

        # Если используется тестовый LocMemCache
        cache.clear()
        print("Кэш очищен через стандартный cache.clear()")

    except Exception as exc:
        print(f"Ошибка при очистке кэша популярных товаров: {exc}")

@receiver(post_save, sender=Product)
def clear_product_cache_after_save(sender, instance, **kwargs):
    clear_popular_products_cache()

@receiver(post_delete, sender=Product)
def clear_product_cache_after_delete(sender, instance, **kwargs):
    clear_popular_products_cache()
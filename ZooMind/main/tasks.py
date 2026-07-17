from celery import shared_task
from datetime import timedelta
from django.utils import timezone


@shared_task
def test_celery_task():
    return "Celery работает"

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_repeat_purchase_reminder(self, order_id):
    from .models import Order

    try:
        order = Order.objects.select_related("owner").get(id=order_id)

        if order.repeat_reminder_sent:
            return f"Напоминание по заказу #{order.id} уже было отправлено"

        username = order.owner.username if order.owner else "Неизвестный пользователь"

        message = f"Напоминание: пользователь {username}, пора повторить покупку по заказу #{order.id}"

        print(message)

        order.repeat_reminder_sent = True
        order.repeat_reminder_sent_at = timezone.now()
        order.save(update_fields=["repeat_reminder_sent", "repeat_reminder_sent_at"])

        return message

    except Order.DoesNotExist:
        return f"Заказ с id={order_id} не найден"

    except Exception as exc:
        raise self.retry(exc=exc)
    
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def check_repeat_purchase_reminders(self):
    from .models import Order

    try:
        reminder_date = timezone.now() - timedelta(days=30)

        orders = (
            Order.objects
            .select_related("owner")
            .filter(
                created_at__lte=reminder_date,
                repeat_reminder_sent=False,
            )
        )

        sent_count = 0

        for order in orders:
            username = order.owner.username if order.owner else "Неизвестный пользователь"

            message = (
                f"Напоминание: пользователь {username}, "
                f"пора повторить покупку по заказу #{order.id}"
            )

            print(message)

            order.repeat_reminder_sent = True
            order.repeat_reminder_sent_at = timezone.now()
            order.save(update_fields=["repeat_reminder_sent", "repeat_reminder_sent_at"])

            sent_count += 1

        return f"Отправлено напоминаний: {sent_count}"

    except Exception as exc:
        raise self.retry(exc=exc)
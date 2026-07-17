from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)

class Pet(models.Model):
    CAT = "Cat"
    DOG = "Dog"
    BIRD = "Bird"

    PET_CHOICES = [
        (CAT, "Кошка"),
        (DOG, "Собака"),
        (BIRD,"Птица")]
    
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="pets",
        null=True,
        blank=True
    )
    name = models.CharField(max_length=25,db_index=True)
    pet_type = models.CharField(max_length=25,choices=PET_CHOICES)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Product(models.Model):
    FOOD = "food"
    MEDiCINE = "medicine"
    TOY = "toy"

    CATEGORY_CHOICES = [
        (FOOD, "Корм"),
        (MEDiCINE, "Лекарство"),
        (TOY, "Игрушки")]
    
    CAT = "cat"
    DOG = "dog"
    BIRD = "bird"

    PET_TYPE_CHOICES = [
        (CAT, "Кошка"),
        (DOG, "Собака"), 
        (BIRD,"Птица")]
    
    pet_type = models.CharField(max_length=30, choices=PET_TYPE_CHOICES, default=CAT)

    category = models.CharField(max_length=30,choices=CATEGORY_CHOICES)
    article = models.CharField(max_length=40,unique=True,db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    name = models.CharField(max_length=25)
    stock_quantity = models.PositiveIntegerField(default=0)

    image = models.ImageField(
    upload_to="products/",
    null=True,
    blank=True
)


    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ["name"]

class PetRecommendation(models.Model):
    pet = models.ForeignKey(
        Pet,
        on_delete=models.CASCADE,
        related_name="recommendations"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="pet_recommendations"
    )
    score = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ("pet","product")
        ordering = ["-score"]
    def __str__(self):
        return f"{self.pet.name} -> {self.product.name}"
class Order(models.Model):
    NEW = "new"
    PAID = "paid"
    CANCELED = "canceled"
    DELIVERED = "delivered"

    STATUS_CHOICES = [
        (NEW, "Новый"),
        (PAID, "Оплачен"),
        (CANCELED, "Отменен"),
        (DELIVERED,"Доставлен")
    ]
    
    owner = models.ForeignKey(
        User,
          on_delete=models.CASCADE,
          related_name="orders"
    )
    products = models.ManyToManyField(
        Product,
        related_name="orders"
    )
    status = models.CharField(
        max_length=25,
        choices=STATUS_CHOICES,
        default=NEW
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    repeat_reminder_sent = models.BooleanField(default=False)
    repeat_reminder_sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"заказ #{self.id}"





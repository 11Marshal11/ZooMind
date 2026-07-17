from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Product, Pet, Order

admin.site.register(User, UserAdmin)
admin.site.register(Product)
admin.site.register(Pet)
admin.site.register(Order)

# Register your models here.

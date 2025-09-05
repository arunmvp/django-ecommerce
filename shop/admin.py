from django.contrib import admin
from .models import Product, CartItem, NewsletterSubscriber

# Register your models here.

admin.site.register(Product)
admin.site.register(CartItem) 
admin.site.register(NewsletterSubscriber)



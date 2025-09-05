from django.db import models
from django.contrib.auth.models import User

# 🛍️ Product Model
class Product(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # 💰 safer than FloatField
    image = models.URLField()
    image2 = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=100)

    def __str__(self):
        return self.title


# 🛒 CartItem Model
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1)



    def __str__(self):
        return f"{self.user.username} - {self.product.title} ({self.quantity})"

    # 💡 Auto calculate subtotal
    @property
    def subtotal(self):
        return self.product.price * self.quantity

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email
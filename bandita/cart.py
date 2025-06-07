from django.conf import settings
from django.db import models
from django.utils import timezone

# 1. Extend or replace Django’s built‑in User
#    You can either use Django’s User directly (from settings.AUTH_USER_MODEL)
#    or swap in your own custom user model with extra fields.
#    Here we’ll assume you’re using the default and just add a profile.

class CustomerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name="profile")
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    # any other metadata you need…

    def __str__(self):
        return f"{self.user.username}"

# 2. Shopping Cart (“Bucket”)
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             null=True, blank=True,
                             on_delete=models.CASCADE,
                             related_name="carts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # optionally: is_active flag to keep historical carts

    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    def total_price(self):
        return sum(item.quantity * item.variant.price for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart,
                             related_name="items",
                             on_delete=models.CASCADE)
    variant = models.ForeignKey('ProductVariant',
                                on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'variant')

# 3. Orders
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('complete', 'Complete'),
        ('canceled', 'Canceled'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20,
                              choices=STATUS_CHOICES,
                              default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2,
                                       blank=True, null=True)
    shipping_address = models.TextField()
    billing_address = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        # Automatically compute total_amount from items
        super().save(*args, **kwargs)
        total = sum(item.quantity * item.variant.price for item in self.items.all())
        if self.total_amount != total:
            self.total_amount = total
            super().save(update_fields=['total_amount'])

class OrderItem(models.Model):
    order = models.ForeignKey(Order,
                              related_name="items",
                              on_delete=models.CASCADE)
    variant = models.ForeignKey('ProductVariant',
                                on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # snapshot the price at order time
        if not self.unit_price:
            self.unit_price = self.variant.price
        super().save(*args, **kwargs)

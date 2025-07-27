# ecommerce_api/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser # For custom user model if needed, but we'll use Django's built-in User for simplicity for now.
# import json # No need to import json here, as TextField stores strings


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100) # In a real app, store hashed passwords!
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    image_url = models.URLField(max_length=255, blank=True, null=True)
    # Changed to TextField for SQLite compatibility
    attributes = models.TextField(default='{}', blank=True, null=True) # Will store JSON as a string

    def __str__(self):
        return self.name


class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Order {self.order_id} by {self.user.email}"


class OrderItem(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.order_id}"


class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.user.email}"


class CartItem(models.Model):
    cart_item_id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Cart {self.cart.cart_id}"


class UserBehavior(models.Model):
    behavior_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='behavior_logs')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ACTION_TYPE_CHOICES = [
        ('View', 'View'),
        ('AddToCart', 'Add To Cart'),
        ('Purchase', 'Purchase'),
    ]
    action_type = models.CharField(max_length=20, choices=ACTION_TYPE_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"User {self.user.email} {self.action_type}ed {self.product.name}"
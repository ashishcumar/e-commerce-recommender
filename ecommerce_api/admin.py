from django.contrib import admin
from .models import User, Product, Order, OrderItem, Cart, CartItem, UserBehavior

admin.site.register(User)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(UserBehavior)
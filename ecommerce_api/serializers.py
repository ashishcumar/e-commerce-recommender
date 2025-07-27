from rest_framework import serializers
from .models import User, Product, Order, OrderItem, Cart, CartItem, UserBehavior

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'name', 'email', 'created_at']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['order_item_id', 'product', 'quantity', 'unit_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True) 

    class Meta:
        model = Order
        fields = ['order_id', 'user', 'order_date', 'total_amount', 'status', 'items']
        read_only_fields = ['order_id', 'order_date', 'total_amount', 'status']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True) 

    class Meta:
        model = CartItem
        fields = ['cart_item_id', 'product', 'quantity', 'added_at']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True) 

    class Meta:
        model = Cart
        fields = ['cart_id', 'user', 'created_at', 'items']

class UserBehaviorSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBehavior
        fields = '__all__'
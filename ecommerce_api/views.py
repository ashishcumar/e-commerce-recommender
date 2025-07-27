# ecommerce_api/views.py

import json # <-- Make sure this is imported
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .models import User, Product, Order, OrderItem, Cart, CartItem, UserBehavior
from .serializers import (
    UserSerializer, ProductSerializer, OrderSerializer, OrderItemSerializer,
    CartSerializer, CartItemSerializer, UserBehaviorSerializer
)


# --- User Views ---
class UserListCreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'user_id'


# --- Product Views ---
class ProductListCreate(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'product_id'


# --- Cart Views ---
class CartDetail(generics.RetrieveAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    lookup_field = 'user__user_id'

    def get_object(self):
        user_id = self.kwargs.get(self.lookup_field)
        user = generics.get_object_or_404(User, user_id=user_id)
        cart, created = Cart.objects.get_or_create(user=user)
        return cart

class AddToCart(APIView):
    def post(self, request, user_id, product_id):
        user = generics.get_object_or_404(User, user_id=user_id)
        product = generics.get_object_or_404(Product, product_id=product_id)

        cart, created = Cart.objects.get_or_create(user=user)
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not item_created:
            cart_item.quantity += 1
            cart_item.save()
        
        UserBehavior.objects.create(user=user, product=product, action_type='AddToCart')

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

class UpdateCartItem(APIView):
    def put(self, request, user_id, product_id):
        user = generics.get_object_or_404(User, user_id=user_id)
        cart = generics.get_object_or_404(Cart, user=user)
        cart_item = generics.get_object_or_404(CartItem, cart=cart, product_id=product_id)

        quantity = request.data.get('quantity')
        if quantity is not None:
            try:
                quantity = int(quantity)
                if quantity > 0:
                    cart_item.quantity = quantity
                    cart_item.save()
                    return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)
                else:
                    cart_item.delete()
                    return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)
            except ValueError:
                return Response({'error': 'Quantity must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Quantity is required.'}, status=status.HTTP_400_BAD_REQUEST)

class RemoveFromCart(APIView):
    def delete(self, request, user_id, product_id):
        user = generics.get_object_or_404(User, user_id=user_id)
        cart = generics.get_object_or_404(Cart, user=user)
        cart_item = generics.get_object_or_404(CartItem, cart=cart, product_id=product_id)
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# --- Order Views ---
class OrderListCreate(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        cart = generics.get_object_or_404(Cart, user=self.request.user)
        total_amount = sum(item.product.price * item.quantity for item in cart.items.all())
        order = serializer.save(user=self.request.user, total_amount=total_amount)
        
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                unit_price=cart_item.product.price
            )
            UserBehavior.objects.create(user=self.request.user, product=cart_item.product, action_type='Purchase')
        
        cart.items.all().delete()

class OrderDetail(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'order_id'


# --- Recommendation Engine View (Similar Products by Category/Attributes) ---
class ProductRecommendations(APIView):
    def get(self, request, product_id, format=None):
        try:
            target_product = Product.objects.get(product_id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        recommended_products = []

        # 1. Recommend products from the same category (strongest similarity)
        similar_by_category = Product.objects.filter(
            category=target_product.category
        ).exclude(product_id=target_product.product_id).distinct()

        for product in similar_by_category:
            if product not in recommended_products:
                recommended_products.append(product)

        # 2. Recommend products with overlapping attributes (Manual parsing for TextField)
        target_product_attributes = {}
        if target_product.attributes:
            try:
                target_product_attributes = json.loads(target_product.attributes)
            except json.JSONDecodeError:
                pass # Handle cases where attributes might not be valid JSON
        
        if target_product_attributes:
            # Get all other products to compare attributes
            # We fetch all, then filter in Python for simplicity with TextField
            other_products_to_compare = Product.objects.exclude(product_id=target_product.product_id)
            
            for other_product in other_products_to_compare:
                other_product_attributes = {}
                if other_product.attributes:
                    try:
                        other_product_attributes = json.loads(other_product.attributes)
                    except json.JSONDecodeError:
                        pass
                
                is_similar_by_attribute = False
                for key, target_value in target_product_attributes.items():
                    # We'll specifically look at 'brand' and 'tags' for simplicity
                    if key == 'brand' and other_product_attributes.get('brand') == target_value:
                        is_similar_by_attribute = True
                        break
                    elif key == 'tags' and isinstance(target_value, list) and 'tags' in other_product_attributes and isinstance(other_product_attributes['tags'], list):
                        # Check for any common tags
                        if any(tag in other_product_attributes['tags'] for tag in target_value):
                            is_similar_by_attribute = True
                            break
                    # You can add more attribute types to compare here (e.g., dimensions, weight, if they are relevant for similarity)
                    # For example:
                    # elif key == 'color' and other_product_attributes.get('color') == target_value:
                    #     is_similar_by_attribute = True
                    #     break
                
                if is_similar_by_attribute:
                    if other_product not in recommended_products:
                        recommended_products.append(other_product)

        # Fallback: If no recommendations based on category/attributes, show trending products
        if not recommended_products:
            trending_product_ids = UserBehavior.objects.filter(action_type='Purchase') \
                                                   .values('product') \
                                                   .annotate(purchase_count=models.Count('product')) \
                                                   .order_by('-purchase_count')[:10]
            trending_products = Product.objects.filter(product_id__in=[item['product'] for item in trending_product_ids])
            
            for product in trending_products:
                 if product not in recommended_products:
                    recommended_products.append(product)
            
            if not recommended_products:
                recommended_products = list(Product.objects.all().order_by('-product_id')[:10])


        serializer = ProductSerializer(recommended_products[:10], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# --- User Behavior Logging (for future enhancements or monitoring) ---
class UserBehaviorListCreate(generics.ListCreateAPIView):
    queryset = UserBehavior.objects.all()
    serializer_class = UserBehaviorSerializer

# Utility view for logging product views
class LogProductView(APIView):
    def post(self, request, user_id, product_id):
        try:
            user = User.objects.get(user_id=user_id)
            product = Product.objects.get(product_id=product_id)
            UserBehavior.objects.create(user=user, product=product, action_type='View')
            return Response({'message': 'Product view logged successfully.'}, status=status.HTTP_200_OK)
        except (User.DoesNotExist, Product.DoesNotExist):
            return Response({'error': 'User or Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
from django.urls import path
from . import views

urlpatterns = [
    # User Endpoints
    path('users/', views.UserListCreate.as_view(), name='user-list-create'),
    path('users/<int:user_id>/', views.UserDetail.as_view(), name='user-detail'),

    # Product Endpoints
    path('products/', views.ProductListCreate.as_view(), name='product-list-create'),
    path('products/<int:product_id>/', views.ProductDetail.as_view(), name='product-detail'),

    # Cart Endpoints
    path('users/<int:user_id>/cart/', views.CartDetail.as_view(), name='cart-detail'),
    path('users/<int:user_id>/cart/add/<int:product_id>/', views.AddToCart.as_view(), name='add-to-cart'),
    path('users/<int:user_id>/cart/update/<int:product_id>/', views.UpdateCartItem.as_view(), name='update-cart-item'),
    path('users/<int:user_id>/cart/remove/<int:product_id>/', views.RemoveFromCart.as_view(), name='remove-from-cart'),

    # Order Endpoints
    path('orders/', views.OrderListCreate.as_view(), name='order-list-create'),
    path('orders/<int:order_id>/', views.OrderDetail.as_view(), name='order-detail'),

    # Recommendation Endpoint
    path('products/<int:product_id>/recommendations/', views.ProductRecommendations.as_view(), name='product-recommendations'),
    
    # User Behavior Logging
    path('users/<int:user_id>/log-view/<int:product_id>/', views.LogProductView.as_view(), name='log-product-view'),
    path('user-behavior/', views.UserBehaviorListCreate.as_view(), name='user-behavior-list-create'),

]
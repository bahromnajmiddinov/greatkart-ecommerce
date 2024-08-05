from django.urls import path

from . import views


urlpatterns = [
    path('', views.cart, name='cart'),
    path('add/<product_id>/', views.add_cart, name='add_cart'),
    path('remove/<cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('increase/<cart_item_id>/', views.increase_cart_item, name='increase_cart_item'),
    path('delete/<cart_item_id>/', views.delete_from_cart, name='delete_from_cart'),
    
    path('checkout/', views.checkout, name='checkout'),
]


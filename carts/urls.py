from django.urls import path

from . import views


urlpatterns = [
    path('', views.cart, name='cart'),
    path('add/<product_id>/', views.add_cart, name='add_cart'),
    path('remove/<cart_id>/', views.remove_cart, name='remove_cart'),
    path('increase/<cart_id>/', views.increase_cart, name='increase_cart'),
    path('delete/<cart_id>/', views.delete_cart, name='delete_cart'),
]


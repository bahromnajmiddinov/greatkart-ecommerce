from django.urls import path

from . import views


urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.dashboard, name='dashboard'),
    # path('profile/', views.profile, name='profile'),
    # path('password_change/', views.password_change, name='password_change'),
    # path('password_reset/', views.password_reset, name='password_reset'),
    # path('password_reset_done/', views.password_reset_done, name='password_reset_done'),
    # path('password_reset_confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    # path('password_reset_complete/', views.password_reset_complete, name='password_reset_complete'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    # path('resend_activation_email/', views.resend_activation_email, name='resend_activation_email'),
]
    

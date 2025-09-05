from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import home, register, login, user_profile, ProductViewSet, CartViewSet, subscribe

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='products')
router.register(r'cart', CartViewSet, basename='cart')

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('profile/', user_profile, name='user_profile'),
    path('subscribe/', subscribe, name='subscribe'),

    path('', include(router.urls)),
]

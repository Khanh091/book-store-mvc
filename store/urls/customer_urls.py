from django.urls import path
from ..controllers.customerController.views import customer_profile, customer_login, customer_logout, customer_register, add_rating

urlpatterns = [
    path('register/', customer_register, name='customer_register'),
    path('login/', customer_login, name='customer_login'),
    path('logout/', customer_logout, name='customer_logout'),
    path('profile/', customer_profile, name='customer_profile'),
    path('rating/add/', add_rating, name='add_rating'),
]
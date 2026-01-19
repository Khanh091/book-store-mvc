from django.urls import path
from ..controllers.staffController.views import (
    staff_login,
    staff_logout,
    staff_dashboard,
    staff_add_book,
)

urlpatterns = [
    path('login/', staff_login, name='staff_login'),
    path('logout/', staff_logout, name='staff_logout'),
    path('dashboard/', staff_dashboard, name='staff_dashboard'),
    path('add_book/', staff_add_book, name='staff_add_book'),
]
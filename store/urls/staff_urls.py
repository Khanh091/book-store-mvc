from django.urls import path
from ..controllers.staffController.views import staff_add_book

urlpatterns = [
    path('add_book/', staff_add_book, name='staff_add_book'),
]
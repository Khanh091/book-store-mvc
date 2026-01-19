from django.urls import path
from ..controllers.bookController.views import book_list, book_detail, book_search, recommend_books

urlpatterns = [
    path('list/', book_list, name='book_list'),
    path('detail/<int:pk>/', book_detail, name='book_detail'),
    path('search/', book_search, name='book_search'),
    path('recommend/', recommend_books, name='recommend_books'),
]
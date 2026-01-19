from django.shortcuts import render, get_object_or_404
from store.models import Book, Customer, Order, Rating

def book_list(request):
    books = Book.objects.all()
    return render(request, 'book/list.html', {'books': books})

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'book/detail.html', {'book': book})

def book_search(request):
    query = request.GET.get('q')
    books = Book.objects.filter(title__icontains=query) if query else []
    return render(request, 'book/search.html', {'books': books})
from store.controllers.customerController.views import customer_required

@customer_required
def recommend_books(request):
    customer = request.customer
    # Gợi ý dựa trên lịch sử order và rating
    from store.models import OrderItem
    bought_books = OrderItem.objects.filter(order__customer=customer).values_list('book_id', flat=True).distinct()
    similar_customers = Rating.objects.filter(book_id__in=bought_books, score__gte=4).values_list('customer', flat=True).distinct()
    recommended = Book.objects.filter(rating__customer__in=similar_customers, rating__score__gte=4).exclude(id__in=bought_books).distinct()[:10]
    return render(request, 'book/recommend.html', {'books': recommended, 'customer': customer})
def home(request):
    return render(request, 'home.html', {'message': 'Welcome to Bookstore Management System'})
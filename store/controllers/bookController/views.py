from django.shortcuts import render, get_object_or_404
from store.models import Book, Customer, Order, Rating
from django.db.models import Avg, Count

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
def recommend_books(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    
    bought_books = Book.objects.filter(orderitem__order__customer=customer).distinct()
    
    if not bought_books.exists():
        popular_books = Book.objects.annotate(
            avg_rating=Avg('rating__score', default=0),
            order_count=Count('orderitem', default=0)
        ).order_by('-avg_rating', '-order_count')[:5]
        return render(request, 'book/recommend.html', {'books': popular_books})
    
    vectors = [b.get_embedding() for b in bought_books if b.get_embedding() is not None]
    if not vectors:
        return render(request, 'book/recommend.html', {'books': []})
    
    avg_vector = np.mean(vectors, axis=0).reshape(1, -1)
    
    unbought_books = Book.objects.exclude(id__in=bought_books.values_list('id', flat=True)).filter(embedding__isnull=False)
    unbought_list = list(unbought_books)
    unbought_vectors = [b.get_embedding() for b in unbought_list]
    
    if not unbought_vectors:
        return render(request, 'book/recommend.html', {'books': []})
    
    unbought_vectors = np.array(unbought_vectors)
    sim_scores = cosine_similarity(avg_vector, unbought_vectors)[0]
    
    top_indices = np.argsort(sim_scores)[::-1][:10]
    top_books = [unbought_list[i] for i in top_indices]
    
    top_books = sorted(
        top_books,
        key=lambda b: Rating.objects.filter(book=b).aggregate(avg=Avg('score'))['avg'] or 0,
        reverse=True
    )[:5]
    
    return render(request, 'book/recommend.html', {'books': top_books})
from django.shortcuts import render, get_object_or_404
from store.models import Book, Customer, Order, Rating
from django.db.models import Avg, Count, Q
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Load model một lần để tối ưu performance
_model = None
def get_embedding_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def book_list(request):
    books = Book.objects.all()
    return render(request, 'book/list.html', {'books': books})

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'book/detail.html', {'book': book})

def book_search(request):
    """Trang search chính"""
    return render(request, 'book/search.html', {'books': [], 'search_type': None})

def book_search_keyword(request):
    """Search keyword: tìm trong title và author"""
    query = request.GET.get('q', '').strip()
    books = []
    if query:
        books = Book.objects.filter(Q(title__icontains=query) | Q(author__icontains=query))
    return render(request, 'book/search.html', {'books': books, 'search_type': 'keyword', 'query': query})

def book_search_vector(request):
    """Search vector: tìm theo semantic similarity"""
    query = request.GET.get('q', '').strip()
    if not query:
        return render(request, 'book/search.html', {'books': [], 'search_type': 'vector', 'query': query})
    
    # Encode query
    model = get_embedding_model()
    query_vector = model.encode(query).reshape(1, -1)
    
    # Lấy sách có embedding
    books_list = list(Book.objects.filter(embedding__isnull=False).exclude(embedding=''))
    book_vectors, valid_books = [], []
    for book in books_list:
        emb = book.get_embedding()
        if emb:
            book_vectors.append(emb)
            valid_books.append(book)
    
    if not book_vectors:
        return render(request, 'book/search.html', {'books': [], 'search_type': 'vector', 'query': query})
    
    # Tính similarity và sắp xếp
    similarities = cosine_similarity(query_vector, np.array(book_vectors))[0]
    results = []
    for idx in np.argsort(similarities)[::-1][:10]:
        if similarities[idx] > 0.1:
            valid_books[idx].similarity_score = round(similarities[idx] * 100, 2)
            results.append(valid_books[idx])
    
    return render(request, 'book/search.html', {'books': results, 'search_type': 'vector', 'query': query})
from store.controllers.customerController.views import customer_required

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
from django.shortcuts import render, get_object_or_404, redirect
from urllib.parse import quote
from store.models import Book, Customer, Order, Rating
from store.controllers.customerController.views import customer_required
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
    """Danh sách sách + tìm kiếm (từ khóa / vector) trên cùng một trang."""
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'keyword').strip().lower()

    if query and search_type == 'vector':
        books = _search_vector(query)
        return render(request, 'book/list.html', {
            'books': books, 'query': query, 'search_type': 'vector'
        })
    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )
        return render(request, 'book/list.html', {
            'books': books, 'query': query, 'search_type': 'keyword'
        })
    books = Book.objects.all()
    return render(request, 'book/list.html', {
        'books': books, 'query': '', 'search_type': None
    })


def _search_vector(query):
    """Tìm sách theo vector (semantic)."""
    books_list = list(Book.objects.filter(embedding__isnull=False).exclude(embedding=''))
    book_vectors, valid_books = [], []
    for book in books_list:
        emb = book.get_embedding()
        if emb:
            book_vectors.append(emb)
            valid_books.append(book)
    if not book_vectors:
        return []
    model = get_embedding_model()
    query_vector = model.encode(query).reshape(1, -1)
    similarities = cosine_similarity(query_vector, np.array(book_vectors))[0]
    results = []
    for idx in np.argsort(similarities)[::-1][:10]:
        if similarities[idx] > 0.1:
            valid_books[idx].similarity_score = round(similarities[idx] * 100, 2)
            results.append(valid_books[idx])
    return results


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'book/detail.html', {'book': book})


def book_search(request):
    """Chuyển hướng sang danh sách sách (tìm kiếm tích hợp)."""
    return redirect('book_list')


def book_search_keyword(request):
    """Redirect: giữ link cũ, chuyển sang book_list với ?q=&type=keyword."""
    q = request.GET.get('q', '').strip()
    if q:
        from django.urls import reverse
        return redirect(reverse('book_list') + '?q=' + quote(q) + '&type=keyword')
    return redirect('book_list')


def book_search_vector(request):
    """Redirect: giữ link cũ, chuyển sang book_list với ?q=&type=vector."""
    q = request.GET.get('q', '').strip()
    if q:
        from django.urls import reverse
        return redirect(reverse('book_list') + '?q=' + quote(q) + '&type=vector')
    return redirect('book_list')
from store.controllers.customerController.views import customer_required

def home(request):
    return render(request, 'home.html', {'message': 'Chào mừng đến với Bookstore'})

@customer_required
def recommend_books(request):
    customer = request.customer
    
    bought_books = Book.objects.filter(orderitem__order__customer=customer).distinct()
    
    if not bought_books.exists():
        popular_books = Book.objects.annotate(
            avg_rating=Avg('rating__score'),
            order_count=Count('orderitem')
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
from django.shortcuts import render, redirect
from store.models import Book

def staff_add_book(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        Book.objects.create(title=title, author=author, price=price, stock_quantity=stock)
        return redirect('book_list')
    return render(request, 'staff/add_book.html')
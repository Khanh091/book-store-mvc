from django.shortcuts import render, redirect
from store.models import Book

def staff_add_book(request):
    if request.method == 'POST':
        title = request.POST['title']
        author = request.POST['author']
        price = request.POST['price']
        stock = request.POST['stock']
        Book.objects.create(title=title, author=author, price=price, stock_quantity=stock)
        return redirect('book_list')
    return render(request, 'staff/add_book.html')
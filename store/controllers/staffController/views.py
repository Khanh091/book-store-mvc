from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from store.models import Book, Staff


def staff_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            staff = Staff.objects.get(email=email, password=password, is_active=True)
            request.session['staff_id'] = staff.id
            return redirect('staff_dashboard')
        except Staff.DoesNotExist:
            messages.error(request, 'Invalid email or password')
    return render(request, 'staff/login.html')


def staff_logout(request):
    request.session.pop('staff_id', None)
    return redirect('home')


def staff_required(view_func):
    def _wrapped(request, *args, **kwargs):
        staff_id = request.session.get('staff_id')
        if not staff_id:
            return redirect('staff_login')
        request.staff = get_object_or_404(Staff, id=staff_id)
        return view_func(request, *args, **kwargs)
    return _wrapped


@staff_required
def staff_dashboard(request):
    books = Book.objects.all()
    return render(request, 'staff/dashboard.html', {'staff': request.staff, 'books': books})


@staff_required
def staff_add_book(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        Book.objects.create(title=title, author=author, price=price, stock_quantity=stock)
        messages.success(request, 'Book added successfully')
        return redirect('staff_dashboard')
    return render(request, 'staff/add_book.html', {'staff': request.staff})
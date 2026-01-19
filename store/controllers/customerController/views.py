from django.shortcuts import render, redirect, get_object_or_404
from store.models import Customer, Rating, Book
from django.contrib import messages

def customer_register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if Customer.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'customer/register.html')
        customer = Customer.objects.create(name=name, email=email, password=password)
        request.session['customer_id'] = customer.id
        return redirect('customer_profile')
    return render(request, 'customer/register.html')

def customer_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            customer = Customer.objects.get(email=email, password=password)
            request.session['customer_id'] = customer.id
            return redirect('customer_profile')
        except Customer.DoesNotExist:
            messages.error(request, 'Invalid email or password')
    return render(request, 'customer/login.html')

def customer_logout(request):
    request.session.pop('customer_id', None)
    return redirect('home')

def customer_profile(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('customer_login')
    customer = get_object_or_404(Customer, id=customer_id)
    return render(request, 'customer/profile.html', {'customer': customer})

def add_rating(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('customer_login')
    if request.method == 'POST':
        customer = get_object_or_404(Customer, id=customer_id)
        book_id = request.POST.get('book_id')
        score = int(request.POST.get('score'))
        book = get_object_or_404(Book, id=book_id)
        rating, created = Rating.objects.get_or_create(
            customer=customer,
            book=book,
            defaults={'score': score}
        )
        if not created:
            rating.score = score
            rating.save()
        return redirect('book_detail', pk=book_id)
    return render(request, 'customer/rating_form.html')
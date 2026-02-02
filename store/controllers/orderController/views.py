from django.shortcuts import render, redirect, get_object_or_404
from store.models import Cart, CartItem, Book, Order, Payment, Shipping, Customer, OrderItem
from store.controllers.customerController.views import customer_required
from django.contrib import messages

@customer_required
def cart_view(request):
    customer = request.customer
    cart, _ = Cart.objects.get_or_create(customer=customer, is_active=True)
    items = CartItem.objects.filter(cart=cart)
    total = sum(float(item.book.price) * item.quantity for item in items)
    return render(request, 'cart/cart.html', {'items': items, 'total': total})

@customer_required
def add_to_cart(request, book_id):
    customer = request.customer
    cart, _ = Cart.objects.get_or_create(customer=customer, is_active=True)
    book = get_object_or_404(Book, id=book_id)
    # Kiểm tra stock
    if book.stock_quantity <= 0:
        messages.error(request, 'Book is out of stock')
        return redirect('book_detail', pk=book_id)
    # Kiểm tra xem sách đã có trong giỏ chưa
    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book, defaults={'quantity': 1})
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart_view')

@customer_required
def buy_now(request, book_id):
    """Add a single book to the cart then go straight to checkout."""
    customer = request.customer
    cart, _ = Cart.objects.get_or_create(customer=customer, is_active=True)
    book = get_object_or_404(Book, id=book_id)
    if book.stock_quantity <= 0:
        messages.error(request, 'Book is out of stock')
        return redirect('book_detail', pk=book_id)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book, defaults={'quantity': 1})
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('checkout')

@customer_required
def checkout(request):
    customer = request.customer
    try:
        cart = Cart.objects.get(customer=customer, is_active=True)
        items = CartItem.objects.filter(cart=cart)
        if not items.exists():
            return redirect('cart_view')
        # Calculate item totals for display
        items_with_total = []
        subtotal = 0
        for item in items:
            item_total = float(item.book.price) * item.quantity
            subtotal += item_total
            items_with_total.append({
                'item': item,
                'total': item_total
            })
        shipping_fee = request.session.get('shipping_fee', 0)
        total = subtotal + shipping_fee
        payment_id = request.session.get('payment_id')
        shipping_id = request.session.get('shipping_id')
        payment = Payment.objects.get(id=payment_id) if payment_id else None
        shipping = Shipping.objects.get(id=shipping_id) if shipping_id else None
        return render(request, 'order/checkout.html', {
            'items_with_total': items_with_total,
            'subtotal': subtotal,
            'shipping_fee': shipping_fee,
            'total': total,
            'payment': payment,
            'shipping': shipping
        })
    except Cart.DoesNotExist:
        return redirect('cart_view')

@customer_required
def select_payment(request):
    if request.method == 'POST':
        payment_id = request.POST.get('payment_id')
        request.session['payment_id'] = payment_id
        return redirect('checkout')
    payments = Payment.objects.all();
    return render(request, 'order/select_payment.html', {'payments': payments})

@customer_required
def select_shipping(request):
    if request.method == 'POST':
        shipping_id = request.POST.get('shipping_id')
        shipping = Shipping.objects.get(id=shipping_id)
        request.session['shipping_id'] = shipping_id
        request.session['shipping_fee'] = float(shipping.fee)
        return redirect('checkout')
    shippings = Shipping.objects.all()
    return render(request, 'order/select_shipping.html', {'shippings': shippings})

@customer_required
def place_order(request):
    customer = request.customer
    try:
        cart = Cart.objects.get(customer=customer, is_active=True)
        items = CartItem.objects.filter(cart=cart)
        
        if not items.exists():
            return redirect('cart_view')
        
        # Kiểm tra stock trước khi đặt hàng
        for item in items:
            if item.book.stock_quantity < item.quantity:
                messages.error(request, f'Not enough stock for {item.book.title}')
                return redirect('cart_view')
        
        # Tính total_price (dùng float cho cùng kiểu với shipping_fee trong session)
        subtotal = sum(float(item.book.price) * item.quantity for item in items)
        shipping_fee = request.session.get('shipping_fee', 0)
        total_price = subtotal + shipping_fee
        
        # Lấy payment và shipping từ session
        payment_id = request.session.get('payment_id')
        shipping_id = request.session.get('shipping_id')
        payment = Payment.objects.get(id=payment_id) if payment_id else None
        shipping = Shipping.objects.get(id=shipping_id) if shipping_id else None
        
        # Tạo Order
        order = Order.objects.create(
            customer=customer,
            total_price=total_price,
            payment=payment,
            shipping=shipping
        )
        
        # Tạo OrderItem cho mỗi sách trong giỏ
        for item in items:
            OrderItem.objects.create(
                order=order,
                book=item.book,
                quantity=item.quantity,
                price=item.book.price
            )
            # Giảm stock
            item.book.stock_quantity -= item.quantity
            item.book.save()
        
        # Vô hiệu hóa giỏ hàng
        cart.is_active = False
        cart.save()
        
        # Xóa session data
        request.session.pop('payment_id', None)
        request.session.pop('shipping_id', None)
        request.session.pop('shipping_fee', None)
        
        return redirect('order_success', order_id=order.id)
    except Cart.DoesNotExist:
        return redirect('cart_view')

@customer_required
def order_success(request, order_id):
    customer = request.customer
    order = get_object_or_404(Order, id=order_id, customer=customer)
    items = OrderItem.objects.filter(order=order)
    return render(request, 'order/success.html', {'order': order, 'items': items})


@customer_required
def my_orders(request):
    """Danh sách đơn hàng của khách với trạng thái giao hàng."""
    customer = request.customer
    orders = Order.objects.filter(customer=customer).order_by('-created_at')
    return render(request, 'order/my_orders.html', {'orders': orders})


@customer_required
def order_detail(request, order_id):
    """Chi tiết đơn hàng và trạng thái giao hàng."""
    customer = request.customer
    order = get_object_or_404(Order, id=order_id, customer=customer)
    items = OrderItem.objects.filter(order=order)
    return render(request, 'order/order_detail.html', {'order': order, 'items': items})

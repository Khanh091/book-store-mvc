from django.db import models
from ..customer.models import Customer
from ..book.models import Book

class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Cart for {self.customer}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.book}"

class Shipping(models.Model):
    method_name = models.CharField(max_length=100)
    fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.method_name

class Payment(models.Model):
    method_name = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default='pending')

    def __str__(self):
        return self.method_name

class Order(models.Model):
    DELIVERY_STATUS_CHOICES = [
        ('pending_carrier', 'Đang chờ đơn vị vận chuyển'),
        ('picked_up', 'Đã lấy hàng'),
        ('in_transit', 'Đang giao'),
        ('delivered', 'Đã giao'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True)
    shipping = models.ForeignKey(Shipping, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    delivery_status = models.CharField(
        max_length=50,
        choices=DELIVERY_STATUS_CHOICES,
        default='pending_carrier'
    )
    delivery_status_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} by {self.customer}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.book.title} in Order {self.order.id}"
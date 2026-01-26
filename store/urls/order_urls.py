from django.urls import path
from ..controllers.orderController.views import cart_view, add_to_cart, buy_now, checkout, select_payment, select_shipping, place_order, order_success

urlpatterns = [
    path('cart/', cart_view, name='cart_view'),
    path('cart/add/<int:book_id>/', add_to_cart, name='add_to_cart'),
    path('checkout/', checkout, name='checkout'),
    path('payment/select/', select_payment, name='select_payment'),
    path('shipping/select/', select_shipping, name='select_shipping'),
    path('place/', place_order, name='place_order'),
    path('success/<int:order_id>/', order_success, name='order_success'),
    path('cart/buy-now/<int:book_id>/', buy_now, name='buy_now'),
]
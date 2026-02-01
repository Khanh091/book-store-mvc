from store.models import Cart, CartItem


def cart_count(request):
    """Thêm số lượng sản phẩm trong giỏ hàng vào mọi template."""
    count = 0
    customer_id = request.session.get('customer_id')
    if customer_id:
        try:
            cart = Cart.objects.get(customer_id=customer_id, is_active=True)
            count = sum(CartItem.objects.filter(cart=cart).values_list('quantity', flat=True))
        except Cart.DoesNotExist:
            pass
    return {'cart_count': count}

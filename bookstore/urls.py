from django.contrib import admin
from django.urls import path, include
from store.controllers.bookController.views import home  # Import view home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('book/', include('store.urls.book_urls')),
    path('customer/', include('store.urls.customer_urls')),
    path('order/', include('store.urls.order_urls')),
    path('staff/', include('store.urls.staff_urls')),
    # Map view home cho path rỗng
    path('', home, name='home'),
]
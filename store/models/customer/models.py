from django.db import models
from ..book.models import Book

class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # Nên dùng Django's User model cho auth thực tế

    def __str__(self):
        return self.name

class Rating(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)  # 1-5

    class Meta:
        unique_together = ('customer', 'book')

    def __str__(self):
        return f"{self.customer} rated {self.book} {self.score}"
from django.db import models
import json

class Book(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.title
    embedding = models.TextField(blank=True, null=True)  # Lưu vector as JSON string: '[0.1, 0.2, ...]'

    def set_embedding(self, vector):
        self.embedding = json.dumps(vector.tolist()) if isinstance(vector, np.ndarray) else json.dumps(vector)

    def get_embedding(self):
        return json.loads(self.embedding) if self.embedding else None
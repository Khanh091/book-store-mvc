from django.db import models

class Staff(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=100, default='staff')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.role})"
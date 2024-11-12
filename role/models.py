from django.db import models


# Create your models here.
class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)


class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    contact_number = models.CharField(max_length=15)
    department = models.CharField(max_length=100)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

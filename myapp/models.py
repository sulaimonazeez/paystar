from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  phone_number = models.CharField(max_length=15, unique=True)
  nin = models.CharField(max_length=12,unique=True)


class VirtualAccounting(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=50)
    order_ref = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.user.username} - {self.account_number}"


class UserProfiles(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  night_mode = models.BooleanField(default=False)
  
  
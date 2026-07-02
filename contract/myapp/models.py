from django.db import models
from django.contrib.auth.models import AbstractUser
 
 
# ---------------- LOGIN ---------------- #
 
class Login(AbstractUser):
    userType = models.CharField(
        max_length=50
    )
 
    viewPass = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
 
    def __str__(self):
        return self.username
 
 
# ---------------- USER (CLIENT) PROFILE ---------------- #
 
class UserProfile(models.Model):
    loginid = models.ForeignKey(
        Login,
        on_delete=models.CASCADE
    )
 
    name = models.CharField(max_length=200)
 
    email = models.EmailField()
 
    phone = models.CharField(max_length=20)
 
    organization = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )
 
    address = models.TextField(
        null=True,
        blank=True
    )
 
    profile_pic = models.ImageField(
        upload_to="user_profiles",
        null=True,
        blank=True
    )
 
    def __str__(self):
        return self.name
    
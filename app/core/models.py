"""
Database models.
"""

from django.db import models
from django.contrib.auth.models import(
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)

class UserManager(BaseUserManager):
   """Create, save and return a new user."""
   def create_user(self, email, password=None, **extra_field):
        if not email:
             raise ValueError("Users must have an email address")
        user = self.model(email=self.normalize_email(email), **extra_field)
        user.set_password(password)
        user.save(using=self._db)
        return user

   def create_superuser(self, email, password=None):
        """Create and return a new superuser"""
        user=self.create_user(email, password)
        user.is_superuser=True
        user.is_staff=True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
   """User in the system."""
   email = models.EmailField(max_length=255, unique=True)
   name = models.CharField(max_length=255)
   is_active = models.BooleanField(default=True)
   is_staff = models.BooleanField(default=False) # Login with Django admin

   objects = UserManager()


   USERNAME_FIELD = "email"

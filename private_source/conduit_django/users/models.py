from django.db import models
from django.contrib.auth.models import AbstractUser,AbstractBaseUser,PermissionsMixin 
from django.contrib.auth.base_user import BaseUserManager
import datetime

class UserManager(BaseUserManager):
    def create_user(self, email, username,password):
        user = User(email=email, username=username)        
        if password: 
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user


    def create_superuser(self, email, username, password=None):
        user = self.create_user(email, username, password)
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100)

    bio = models.TextField(null = True, blank=True)
    image = models.CharField(max_length=100, null = True, blank=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.email
       
    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    objects = UserManager()
    EMAIL_FIELD = "email"

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="follow_follower")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="follow_user")


# https://docs.djangoproject.com/en/5.1/topics/auth/customizing/#top
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,AbstractUser
from users.models import User
from django.conf import settings 
# Create your models here.

class Tag(models.Model):
    name =  models.CharField()

class Article(models.Model):
    slug = models.SlugField(max_length=100)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=False)
    body = models.TextField()
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    favorited = models.BooleanField()
    favoritesCount = models.IntegerField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    

    
# {
#   "article": {
#     "slug": "how-to-train-your-dragon",
#     "title": "How to train your dragon",
#     "description": "Ever wonder how?",
#     "body": "It takes a Jacobian",
#     "tagList": ["dragons", "training"],
#     "createdAt": "2016-02-18T03:22:56.637Z",
#     "updatedAt": "2016-02-18T03:48:35.824Z",
#     "favorited": false,
#     "favoritesCount": 0,
#     "author": {
#       "username": "jake",
#       "bio": "I work at statefarm",
#       "image": "https://i.stack.imgur.com/xHWG8.jpg",
#       "following": false
#     }
#   }
# }
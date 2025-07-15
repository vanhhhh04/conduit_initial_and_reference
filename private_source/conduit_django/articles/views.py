from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.http import HttpResponse
from django.conf import settings 
from django.shortcuts import get_object_or_404

import logging

from .models import Article,Tag
from .forms import ArticleCreateForm,ArticleUpdateForm
from users.models import User
from users.authentication import decode_jwt
import json 
import time 
from django.utils.text import slugify

form_error_logger = logging.getLogger('form_errors')

@csrf_exempt
@require_http_methods(['GET','POST'])
def list_and_create_articles(request):
    if request.method == "GET":
        tag = request.GET.get("tag")
        author = request.GET.get("author")
        favorited = request.GET.get("favorited")
        articles = Article.objects.all()
        if tag:
            articles = Article.objects.filter(tags__name__contains=f"{tag}")
        if author:
            articles = Article.objects.filter(author__username__contains=f"{author}")
        if favorited:
            articles = Article.objects.filter(favorites__username__contains=favorited) 
        
        data_response = []
        for article in articles:
            data_response.append({
                "id": article.id,
                "slug": article.slug,
                "title": article.title,
                "description": article.description,
                "tagList": [tag.name for tag in article.tags.all()],
                "createdAt": article.createdAt,
                "updatedAt": article.updatedAt,
                "favorited": False,
                "favoritesCount": article.favoritesCount,
                "author":{
                    "username": article.author.username,
                    "bio": article.author.bio,
                    "image": article.author.image,
                    "following": False
                }
                })   
        return JsonResponse({"articles": data_response, "articlesCount": len(data_response)})
    if request.method == "POST":
        payload_data = None
        
        # Check Authorization header
        if "HTTP_AUTHORIZATION" in request.META:
            token = request.META["HTTP_AUTHORIZATION"]
            if token.startswith("Token "):
                token_sanitize = token[6:]
                payload_data = decode_jwt(token_sanitize)
            else:
                return JsonResponse({"error": "Invalid token format"}, status=400)
        else:
            return JsonResponse({"error": "Authorization header required"}, status=401)
        
        # Get user from payload
        if payload_data and payload_data.get('user_id'):
            try:
                request.user = User.objects.get(id=payload_data.get('user_id'))
            except User.DoesNotExist:
                return JsonResponse({"error": "Invalid user in token"}, status=401)
        else:
            return JsonResponse({"error": "Invalid token payload"}, status=400)
        
        # Decode JSON body
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON")
        
        data = data.get("article")
        if data:
            form = ArticleCreateForm(data)
            if form.is_valid():
                title = form.cleaned_data['title']
                description = form.cleaned_data['description']
                body = form.cleaned_data['body']
                tagList = form.cleaned_data.get('tagList', [])
                tagList = tagList if isinstance(tagList, list) else []

                tagList_objects = Tag.objects.filter(name__in=tagList)

                new_article = Article.objects.create(
                    slug=title.replace(" ","-"), 
                    title=title,
                    description=description,
                    body=body,
                    favorited=False,
                    favoritesCount=0,
                    author=request.user  
                )

                new_article.tags.add(*tagList_objects)

                return JsonResponse({
                    "article": {
                        "slug": new_article.slug,
                        "title": new_article.title,
                        "description": new_article.description,
                        "body": new_article.body,
                        "tags": [tag.name for tag in new_article.tags.all()],
                        "createdAt":new_article.createdAt,
                        "updatedAt":new_article.updatedAt,
                        "favorited": new_article.favorited,
                        "favoritesCount": new_article.favoritesCount,
                        "author": {
                            "username": request.user.username,
                            "bio": request.user.bio,
                            "image": request.user.image,
                            "following": False
                        }
                    }
                })
            else:
                return JsonResponse({"errors": form.errors}, status=400)
        else:
            return HttpResponseBadRequest("No article data")

@csrf_exempt
@require_http_methods(['GET'])
def list_favorited_articles(request):
    if request.method == 'GET':
        print("article feed")
        if "HTTP_AUTHORIZATION" in request.META:
            token = request.META["HTTP_AUTHORIZATION"]
            if token.startswith("Token "):
                token_sanitize = token[6:]
                payload_data = decode_jwt(token_sanitize)
            else:
                return JsonResponse({"error": "Invalid token format"}, status=400)
        else:
            return JsonResponse({"error": "Authorization header required"}, status=401)
        
        # Get user from payload
        if payload_data and payload_data.get('user_id'):
            try:
                request.user = User.objects.get(id=payload_data.get('user_id'))
            except User.DoesNotExist:
                return JsonResponse({"error": "Invalid user in token"}, status=401)
        else:
            return JsonResponse({"error": "Invalid token payload"}, status=400)
        articles = Article.objects.filter(favorites__id=request.user.id)
        data_response = []
        for article in articles:
            data_response.append({
                "id": article.id,
                "slug": article.slug,
                "title": article.title,
                "description": article.description,
                "tagList": [tag.name for tag in article.tags.all()],
                "createdAt": article.createdAt,
                "updatedAt": article.updatedAt,
                "favorited": False,
                "favoritesCount": article.favoritesCount,
                "author":{
                    "username": article.author.username,
                    "bio": article.author.bio,
                    "image": article.author.image,
                    "following": False
                }
                })   
        return JsonResponse({"articles": data_response, "articlesCount": len(data_response)})


@csrf_exempt
@require_http_methods(['PUT','GET','DELETE'])
def get_and_update_and_delete_article(request, slug):
    # Get article by slug
    if request.method == 'PUT':
        article_rec = get_object_or_404(Article, slug=slug)
        
        # Check Authorization header
        if "HTTP_AUTHORIZATION" in request.META:
            token = request.META["HTTP_AUTHORIZATION"]
            if token.startswith("Token "):
                token_sanitize = token[6:]
                payload_data = decode_jwt(token_sanitize)
            else:
                return JsonResponse({"error": "Invalid token format"}, status=400)
        else:
            return JsonResponse({"error": "Authorization header required"}, status=401)
        
        # Get user from payload
        if payload_data and payload_data.get('user_id'):
            try:
                request.user = User.objects.get(id=payload_data.get('user_id'))
            except User.DoesNotExist:
                return JsonResponse({"error": "Invalid user in token"}, status=401)
        else:
            return JsonResponse({"error": "Invalid token payload"}, status=400)
        
        # Check ownership
        if article_rec.author != request.user:
            return JsonResponse({"error": "User is not permitted to update this article"}, status=403)
        
        # Decode JSON
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON")
        
        # Update article fields
        article_data = data.get("article")
        if article_data:
            updateform = ArticleUpdateForm(article_data)
            if updateform.is_valid():
                for field, value in updateform.cleaned_data.items():
                    setattr(article_rec, field, value)
                title_value = updateform.cleaned_data.get("title","")
                if title_value:
                    article_rec.slug = slugify(title_value)
                # Handle tags
                # Rehandle this point 
                tagList = article_data.get("tagList", [])
                if isinstance(tagList, list):
                    tag_objects = Tag.objects.filter(name__in=tagList)
                    article_rec.tags.clear()
                    article_rec.tags.add(*tag_objects)
                
                article_rec.save()
                data_response = {
                "slug": article_rec.slug,
                "title": article_rec.title,
                "description": article_rec.description,
                "body": article_rec.body,
                "tagList": [tag.name for tag in article_rec.tags.all()],
                "createdAt": article_rec.createdAt,
                "updatedAt": article_rec.updatedAt,
                "favorited": False,
                "favoritesCount": article_rec.favoritesCount,
                "author":{
                    "username": article_rec.author.username,
                    "bio": article_rec.author.bio,
                    "image": article_rec.author.image,
                    "following": False
                }
                }
                return JsonResponse({"article": data_response},status=200)
            else:
                return JsonResponse({"errors": updateform.errors}, status=400)
        else:
            return JsonResponse({"error": "No article data provided"}, status=400)
    if request.method == 'GET':
        article_rec = get_object_or_404(Article, slug=slug)
        print(article_rec)
        data_response = {
        "slug": article_rec.slug,
        "title": article_rec.title,
        "description": article_rec.description,
        "body": article_rec.body,
        "tagList": [tag.name for tag in article_rec.tags.all()],
        "createdAt": article_rec.createdAt,
        "updatedAt": article_rec.updatedAt,
        "favorited": False,
        "favoritesCount": article_rec.favoritesCount,
        "author":{
            "username": article_rec.author.username,
            "bio": article_rec.author.bio,
            "image": article_rec.author.image,
            "following": False
        }
        }
        
        return JsonResponse({"article": data_response})
    if request.method == 'DELETE':
        article_rec = get_object_or_404(Article, slug=slug)
        
        # Check Authorization header
        if "HTTP_AUTHORIZATION" in request.META:
            token = request.META["HTTP_AUTHORIZATION"]
            if token.startswith("Token "):
                token_sanitize = token[6:]
                payload_data = decode_jwt(token_sanitize)
            else:
                return JsonResponse({"error": "Invalid token format"}, status=400)
        else:
            return JsonResponse({"error": "Authorization header required"}, status=401)
        
        # Get user from payload
        if payload_data and payload_data.get('user_id'):
            try:
                request.user = User.objects.get(id=payload_data.get('user_id'))
            except User.DoesNotExist:
                return JsonResponse({"error": "Invalid user in token"}, status=401)
        else:
            return JsonResponse({"error": "Invalid token payload"}, status=400)
        
        # Check ownership
        if article_rec.author != request.user:
            return JsonResponse({"error": "User is not permitted to update this article"}, status=403)
        article_rec.delete()
        return JsonResponse({"Sucess":"Delete Success article"})


@csrf_exempt
@require_http_methods(['POST','DELETE'])
def favorite_unfavorite_article(request, slug):
    article_rec = get_object_or_404(Article, slug=slug)
    
    # Check Authorization header
    if "HTTP_AUTHORIZATION" in request.META:
        token = request.META["HTTP_AUTHORIZATION"]
        if token.startswith("Token "):
            token_sanitize = token[6:]
            payload_data = decode_jwt(token_sanitize)
        else:
            return JsonResponse({"error": "Invalid token format"}, status=400)
    else:
        return JsonResponse({"error": "Authorization header required"}, status=401)
    
    # Get user from payload
    if payload_data and payload_data.get('user_id'):
        try:
            request.user = User.objects.get(id=payload_data.get('user_id'))
        except User.DoesNotExist:
            return JsonResponse({"error": "Invalid user in token"}, status=401)
    else:
        return JsonResponse({"error": "Invalid token payload"}, status=400)    
    if request.method == 'POST':
        article_rec.favorites.add(request.user)
        
    if request.method == 'DELETE':
        article_rec.favorites.remove(request.user)
    data_response = {
        "id": article_rec.id,
        "slug": article_rec.slug,
        "title": article_rec.title,
        "description": article_rec.description,
        "tagList": [tag.name for tag in article_rec.tags.all()],
        "createdAt": article_rec.createdAt,
        "updatedAt": article_rec.updatedAt,
        "favorited": False,
        "favoritesCount": article_rec.favoritesCount,
        "author":{
            "username": article_rec.author.username,
            "bio": article_rec.author.bio,
            "image": article_rec.author.image,
            "following": False
        }
        }
    return JsonResponse({"article": data_response})


@csrf_exempt
@require_http_methods(['GET'])
def list_tag(request):
    all_tags = Tag.objects.all()
    
    data_response = [tag_name.name for tag_name in all_tags]
    return JsonResponse({"tags":data_response}, status=200)
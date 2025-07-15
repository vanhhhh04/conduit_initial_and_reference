from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import get_object_or_404

import logging

# Create your views here.
from .forms import UserForm,UserUpdateForm
from .models import User,Follow
from .authentication import encode_jwt,decode_jwt
# from rest_framework.authtoken.models import Token

import json 
import time 

form_error_logger = logging.getLogger('form_errors')

@csrf_exempt
@require_http_methods(['POST'])
def user_login(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    user_data = data.get('user', {})
    form = UserForm(user_data, is_login=True)

    if form.is_valid():
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({"error": "Invalid credentials"}, status=401)
        print("[AAAA]")
        if not check_password(password, user.password):
            print("[CCCC]")
            return JsonResponse({"error": "Invalid credentials"}, status=401)

        payload = {
            'user_id': user.id,
            'username': user.username,
            'exp': int(time.time()) + 3600
        }
        print("[BBBB]")
        token = encode_jwt(payload)

        response_data = form.to_response_data(user, token)
        # {
            # 'id': user.id,
            # 'username': user.username,
            # 'email': user.email,
            # 'token': token
        # }
        return JsonResponse({"user": response_data}, status=200)

    else:
        print("BBBB")
        print("Form errors:", form.errors.as_json())  # ADD THIS LINE
        form_error_logger.error(f"Form validation errors: {form.errors.as_json()}")
        print(form.errors.as_json())
        return JsonResponse({"errors": form.errors}, status=400)



@csrf_exempt
@require_http_methods(['POST'])
def user_register(request):
    if request.method == "POST":
        try :
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON")
        data = data.get('user',{})
        form = UserForm(data)
        try: 
            if form.is_valid():
                form_data = form.cleaned_data 
                email = form_data.get('email')
                username = form_data.get('username')
                password = form_data.get('password')          

                user = User.objects.create(
                    username = username,
                    email = email,
                    password = make_password(password)
                )
                
                payload = {
                    'user_ud': user.id,
                    'username': user.username,
                    'exp': int(time.time()) + 3600
                }
                
                token = encode_jwt(payload)
                print(token)
                response_data = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'token': token 
                }
                return JsonResponse({"user": response_data}, status=200)
            else:
                return JsonResponse({"erros": form.errors}, status=400)
        except Exception as e:
            raise e 
        


@csrf_exempt
@require_http_methods(['GET','PUT'])
def get_and_update_user(request):
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
    if request.method == 'GET':
        payload = {
            'user_id': request.user.id,
            'username': request.user.username,
            'exp': int(time.time()) + 3600
        }
        token = encode_jwt(payload)
        response_data = {
                'email': request.user.email,
                'token': token,
                'username': request.user.username,
                "bio": request.user.bio,
                "image": request.user.image,
            }

        return JsonResponse({"user": response_data}, status=200)
    if request.method == 'PUT':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON")
        
        # Update article fields
        user_data = data.get("user")
        if user_data:
            updateform = UserUpdateForm(user_data)
            if updateform.is_valid(): 
                for field,value in updateform.cleaned_data.items():
                    setattr(request.user, field,value)
                request.user.save()
        payload = {
            'user_id': request.user.id,
            'username': request.user.username,
            'exp': int(time.time()) + 3600
        }
        token = encode_jwt(payload)
        response_data = {
                'email': request.user.email,
                'token': token,
                'username': request.user.username,
                "bio": request.user.bio,
                "image": request.user.image,
            }

        return JsonResponse({"user": response_data}, status=200)
# Adding logic following 
@csrf_exempt
@require_http_methods(['GET'])
def get_profiles(request,username):
    if request.method == 'GET':
        user_profile = User.objects.filter(username=f"{username}")
        get_object_or_404(user_profile)
        data_response = {
            "username": user_profile.username,
            "bio": user_profile.bio,
            "image": user_profile.image,
            "following": False
        }       
        return JsonResponse({"profile":data_response}, status=200)


@csrf_exempt
@require_http_methods(['POST,DELETE'])
def follow_unfollow_user(request,username):
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
    followed_user = User.objects.filter(username=f"{username}")
    get_object_or_404(followed_user)
    follower = request.user 
    if request.method == 'POST':
        if Follow.objects.filter(follower=follower,user=followed_user).exists():
            pass 
        else:
            Follow.objects.create(follower=follower, user=follower)
    if request.method == 'DELETE':
        follow_rec = Follow.objects.filter(follower=follower,user=followed_user)
        if follow_rec.exists():
           follow_rec.delete()
    data_response = {
        "username": followed_user.username,
        "bio": followed_user.bio,
        "image": followed_user.image,
        "following": False
        }       
    return JsonResponse({"profile":data_response}, status=200) 
        
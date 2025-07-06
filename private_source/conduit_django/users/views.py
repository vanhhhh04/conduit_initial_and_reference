from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
import logging

# Create your views here.
from .forms import UserForm 
from .models import User 
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
        





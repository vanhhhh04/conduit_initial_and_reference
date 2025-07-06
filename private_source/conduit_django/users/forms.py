from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("email",)


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ("email",)

class UserForm(forms.Form):
    email = forms.EmailField(max_length=100)
    username = forms.CharField(max_length=100)
    password = forms.CharField(max_length=100)

    def __init__(self, *args, **kwargs):
        is_login = kwargs.pop('is_login', False)  # custom flag
        super(UserForm, self).__init__(*args, **kwargs)
        if is_login:
            self.fields['username'].required = False
    
    def to_response_data(self, user, token):
        return {
            'id': user.id,
            'username': user.username,
            'email': self.cleaned_data.get('email'),
            'token': token
        }
    # def clean_username(self):
    #     username = self.cleaned_data["username"]
    #     if not username.startswith("AAA"):
    #         raise ValidationError("your username is not valid")
    #     return username
     

    
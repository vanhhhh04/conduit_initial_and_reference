from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User


class ArticleCreateForm(forms.Form):
    title = forms.CharField(max_length=100)
    description = forms.CharField(max_length=100)
    body = forms.CharField(max_length=100)
    tagList = forms.Field(required=False)
    
    
    def clean_tagList(self):
        tag_list = self.cleaned_data['tagList']
        if not isinstance(tag_list, list):
            raise forms.ValidationError("TagList must be a list of strings")
        return tag_list
        
class ArticleUpdateForm(forms.Form):
    title = forms.CharField(max_length=100, required=False)
    description = forms.CharField(max_length=100, required=False)
    body = forms.CharField(max_length=100, required=False)
    tagList = forms.Field(required=False)
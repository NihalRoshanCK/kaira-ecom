from django import forms
from .models import UserProfile
from django.contrib.auth.models import User

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('mobile', 'address','district', 'state', 'pincode', 'image',)
        widgets = {
            'mobile': forms.TextInput(attrs={'class' : 'form-control','minlength': 10, 'maxlength': 10}),
            'address':forms.TextInput(attrs={'class' : 'form-control'}),
            'district':forms.Select(attrs={'class' : 'form-control'}),
            'state':forms.Select(attrs={'class' : 'form-control'}),
            'pincode':forms.TextInput(attrs={'class' : 'form-control','minlength': 6, 'maxlength': 6}),
            'image':forms.FileInput(attrs={'class' : 'form-control'}),
    
    }

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name','username')
        widgets = {
            'first_name': forms.TextInput(attrs={'class' : 'form-control'}),
            'last_name' : forms.TextInput(attrs={'class' : 'form-control'}),
            'username' : forms.TextInput(attrs={'class' : 'form-control'}),
            
        }
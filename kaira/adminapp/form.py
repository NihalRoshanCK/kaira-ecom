from django import forms
from product.models import Coupon

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount', 'min_value', 'valid_from', 'valid_at', 'active']
        widgets = {
            'valid_from': forms.DateTimeInput(attrs={'type': 'datetime-local','placeholder': 'First Name', 'class':'form-control bg-white','style':'max-width:300px;'}),
            'valid_at': forms.DateTimeInput(attrs={'type': 'datetime-local','placeholder': 'First Name','class':'form-control bg-white', 'style':'max-width:300px;'}),
            'code': forms.TextInput(attrs={'placeholder': 'Coupon code', 'class': 'form-control bg-white','style':'max-width:300px;'}),
            'discount': forms.NumberInput(attrs={'placeholder': 'Discount', 'class': 'form-control bg-white','style':'max-width:300px;'}),
            'min_value': forms.NumberInput(attrs={'placeholder': 'Minimum value', 'class': 'form-control bg-white','style':'max-width:300px;'}),
}
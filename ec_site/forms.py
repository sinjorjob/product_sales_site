from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User
from django.core.exceptions import ValidationError


class LoginForm(AuthenticationForm):
    """ログインフォーム"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

class SignUpForm(UserCreationForm):
    """ユーザー登録用フォーム"""

    class Meta:
        model = User
        fields = ('email', 'name',)
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class ShoppingCartDetailForm(forms.Form):

    name = forms.CharField(label="氏名")
    email = forms.EmailField(label="メールアドレス")
    zip_code = forms.RegexField(
        label="郵便番号",
        regex=r'^[0-9]+$',
        max_length=8,
        help_text = '※郵便番号のハイフン「-」なしでも可',
        widget=forms.TextInput(attrs={
            'onKeyUp' : "AjaxZip3.zip2addr(this,'','address','address')"}),)
    address = forms.CharField(label="住所",help_text="※郵便番号を入力すると市区町村まで自動で入力されます。")
    
    
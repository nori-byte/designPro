from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
import re
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=100,
        label='ФИО',
    )
    email = forms.EmailField(
        label='Email',
    )
    username = forms.CharField(
        label='Логин',
    )
    agreement = forms.BooleanField(
        required=True,
        label='Согласие на обработку персональных данных',
    )

    class Meta:
        model = CustomUser
        fields = ('full_name', 'username', 'email', 'password1', 'password2', 'agreement')

    def clean_full_name(self):
        full_name = self.cleaned_data['full_name']
        if not re.match(r'^[а-яА-ЯёЁ\s\-]+$', full_name):
            raise ValidationError('ФИО должно содержать только кириллические буквы, пробелы и дефис')
        return full_name

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.match(r'^[a-zA-Z\-]+$', username):
            raise ValidationError('Логин должен содержать только латинские буквы и дефис')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким логином уже существует')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='Логин',
    )
    password = forms.CharField(
        label='Пароль',
    )
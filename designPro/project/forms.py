import os

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
import re

from django.core.validators import FileExtensionValidator
from pip._internal.utils.filesystem import file_size

from .models import CustomUser, DesignRequest


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

        def file_size(value):
            limit = 2 * 1024 * 1024
            if value.size > limit:
                raise ValidationError('Размер файла не должен превышать 2Мб.')

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
        widget=forms.PasswordInput()
    )


class DesignRequestForm(forms.ModelForm):
    class Meta:
        model = DesignRequest
        fields = ['title', 'description', 'category', 'image']
        labels = {'image': 'Фото помещения или план'}
        image = forms.FileField(
            validators=[file_size, FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'bmp'])],
            label='Изображение')

class StatusChange(forms.Form):
    STATUS_CHOICES = [
        ('i', 'Принято в работу'),
        ('c', 'Выполнено')
    ]
    new_status = forms.ChoiceField(choices=STATUS_CHOICES, label="Новый статус заявки")
    description = forms.CharField(required=False, label="Комментарий (обязателен для 'Принято в работу')")
    comment_image = forms.ImageField(required=False, label="Изображение дизайна (обязательно для 'Выполнено')")

    def clean(self):
        cleaned_data = super().clean()
        new_status = cleaned_data.get('new_status')
        description = cleaned_data.get('description')
        comment_image = cleaned_data.get('comment_image')

        if new_status == 'i' and not description:
            raise ValidationError("Комментарий обязателен для смены статуса на 'Принято в работу'.")
        elif new_status == 'c' and not comment_image:
            raise ValidationError("Изображение дизайна обязательно для смены статуса на 'Выполнено'.")

        return cleaned_data
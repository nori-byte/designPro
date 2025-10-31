from django.shortcuts import render
from django.contrib.auth.views import LoginView

from .forms import OrderForm


def main_page(request):
    return render(request, template_name='main.html')


def flight_details(request):
    form = OrderForm()
    ship_images = [ship.image.url for ship in form.fields['ship'].queryset]
    ship_field = zip(form['ship'], ship_images)
    if request.method == 'POST':
        form = OrderForm(data=request.POST)
    return render(
        request,
        template_name='ship.html',
        context={
            'space_form': form,
            'ship_field': ship_field
        }
    )

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages


# Регистрация
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            # Проверяем, нет ли такого пользователя
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password=password)
                login(request, user)
                messages.success(request, f'Аккаунт {username} создан!')
                return redirect('main_page')
            else:
                messages.error(request, 'Это имя уже занято')

    return render(request, 'register.html')


# Вход
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {username}!')
            return redirect('main_page')
        else:
            messages.error(request, 'Неверное имя или пароль')

    return render(request, 'login.html')


# Выход
def user_logout(request):
    logout(request)
    messages.success(request, 'Вы вышли из системы')
    return redirect('main_page')

амаа
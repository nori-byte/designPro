# from django.shortcuts import render
# from django.contrib.auth.views import LoginView
#
#
# def main_page(request):
#     return render(request, template_name='main.html')
#
# from django.shortcuts import render, redirect
# from django.contrib.auth import login, logout, authenticate
# from django.contrib.auth.models import User
# from django.contrib import messages
#
#
# # Регистрация
# def register(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#
#         if username and password:
#             # Проверяем, нет ли такого пользователя
#             if not User.objects.filter(username=username).exists():
#                 user = User.objects.create_user(username=username, password=password)
#                 login(request, user)
#                 messages.success(request, f'Аккаунт {username} создан!')
#                 return redirect('main_page')
#             else:
#                 messages.error(request, 'Это имя уже занято')
#
#     return render(request, 'register.html')
#
#
# # Вход
# def user_login(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#
#         user = authenticate(username=username, password=password)
#         if user:
#             login(request, user)
#             messages.success(request, f'Добро пожаловать, {username}!')
#             return redirect('main_page')
#         else:
#             messages.error(request, 'Неверное имя или пароль')
#
#     return render(request, 'login.html')
#
#
# # Выход
# def user_logout(request):
#     logout(request)
#     messages.success(request, 'Вы вышли из системы')
#     return redirect('main_page')

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm



def is_admin(user):
    return user.is_staff


# Главная страница
def main(request):
    return render(request, 'main.html')


# Регистрация через форму
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Регистрация прошла успешно! Добро пожаловать, {user.full_name}!')

            if user.is_staff:
                return redirect('admin_dashboard')
            return redirect('profile')
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})



def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')

            if user.is_staff:
                return redirect('admin_dashboard')
            return redirect('profile')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'login.html', {'form': form})



def user_logout(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('main_page')


# Личный кабинет пользователя
@login_required
def profile(request):
    return render(request, 'profile.html')


# # Панель администратора
# @user_passes_test(is_admin)
# def admin_dashboard(request):
#     users = CustomUser.objects.all()
#     return render(request, 'admin_dashboard.html', {'users': users})

def main_page(request):
    return render(request, 'main.html')
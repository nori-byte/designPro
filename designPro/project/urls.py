from django.urls import path
from . import views

from .views import main_page


urlpatterns = [
    path('', main_page, name='main_page'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
]
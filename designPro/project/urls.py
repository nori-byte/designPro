from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('admin-dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('create-request/', views.create_request, name='create_request'),
    path('my-requests/', views.my_requests, name='my_requests'),
    path('request/<int:pk>/', views.request_detail, name='detail_request'),
    path('request/<int:pk>/delete/', views.delete_request, name='delete_request'),
    path('admin-dashboard/dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin-dashboard/request/<int:pk>/change-request-status/', views.change_request_status, name='change_request_status'),
    path('admin-dashboard/category/add/', views.add_category, name='add_category'),
    path('admin-dashboard/category/<int:pk>/delete/', views.delete_category, name='delete_category'),
]

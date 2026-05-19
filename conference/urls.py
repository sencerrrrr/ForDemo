from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('accounts/login', views.login_view, name='login'),
    path('accounts/register', views.register_view, name='register'),
    path('accounts/logout', views.logout_view, name='logout'),
    path('accounts/dashboard/', views.dashboard_view, name='dashboard'),
    path('requests/create/', views.create_request_view, name='create_request'),
    path('requests/<int:pk>/review/', views.review_create_view, name='review_create'),
    path('control/requests/', views.admin_requests_view, name='admin_requests'),
    path('control/requests/<int:pk>/', views.admin_request_detail_view, name='admin_request_detail'),
]

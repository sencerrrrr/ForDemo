from django.contrib import messages
from django.contrib.auth import logout, login
from django.shortcuts import render, redirect


def check_admin_access(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if not request.user.is_staff:
        messages.error(request, 'Доступ разрешён только администратору.')
        return redirect('login')

    return None


def home_view(request):
    return render(request, 'conference/home.html')


def login_view(request):
    return render(request, 'conference/login.html')


def register_view(request):
    return render(request, 'conference/register.html')


def logout_view(request):
    logout(request)
    return redirect('login')
from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from .models import Users

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        user_type = 'S'
        middle_name = request.POST.get('middle_name')

        # checking user already exist or not
        if Users.objects.filter(username=username).exists():
            error_message = 'Username already exists'
            return render(request, 'register.html', {'error_message': error_message})

        user = Users.objects.create_user(username=username, password=password, email=email, user_type=user_type, middle_name=middle_name)
        return redirect('login')

    else:
        return render(request, 'register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authentication of the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('product')
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
    else:
        return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return render(request, 'register.html')

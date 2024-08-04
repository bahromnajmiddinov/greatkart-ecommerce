from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Account
from .forms import AccountForm


def register(request):
    form = AccountForm()
    
    if request.method == 'POST':
        form = AccountForm(request.POST)
        
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            phone_number = form.cleaned_data.get('phone_number')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            username = email.split('@')[0]
            
            counter = 1
            while Account.objects.filter(username=username).exists():
                username += counter
                counter += 1
            
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, 
                                               password=password, email=email, username=username)
            user.phone_number = phone_number
            user.save()
            
            messages.success(request, 'Account created successfully')
            
            return redirect('login')
        
    return render(request, 'accounts/register.html', {'form': form})


def login(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        email = request.POST.get('email')
        user = authenticate(email=email, password=password)
        
        if user is not None:
            auth_login(request, user)
            messages.success(request, 'Logged in successfully')
            return redirect('home')
        
        messages.error(request, 'Invalid credentials')
    
    return render(request, 'accounts/signin.html')


@login_required(login_url='login')
def logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully')
    return render(redirect('login'))



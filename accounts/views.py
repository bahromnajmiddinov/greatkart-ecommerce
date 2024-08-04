from config import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, logout, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import send_mail

from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from .models import Account
from .forms import AccountForm


@login_required(login_url='login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')


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
            
            # USER ACTIVATION EMAIL
            current_site = get_current_site(request)
            activation_url = reverse('activate', kwargs={'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                                                          'token': default_token_generator.make_token(user)})
            message = render_to_string('accounts/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'protocol': 'https' if request.is_secure() else 'http',
                'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            send_mail(
                subject='Activate your GreatKart Account',
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
            
            messages.success(request, 'Account created successfully. Please check your email for the activation link.')
            
            redirect_url = reverse('login') + f'?confirmationemail={ email }?command=activate'
            return redirect(redirect_url)
        
    return render(request, 'accounts/register.html', {'form': form})


def login(request):
    confirmationemail = request.GET.get('confirmationemail')
    
    if request.method == 'POST':
        password = request.POST.get('password')
        email = request.POST.get('email')
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                messages.success(request, 'Logged in successfully')
                return redirect('dashboard')
            else:
                messages.info(request, 'Your account is not active. Please check your email for the activation link.')
        else:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'accounts/signin.html', {'confirmationemail': confirmationemail})


@login_required(login_url='login')
def logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully')
    return render(redirect('login'))


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Account activated successfully')
        return redirect('login')
    
    messages.error(request, 'Activation link is invalid or expired')
    return render(request, 'accounts/activation_error.html')


def password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = Account.objects.filter(email=email).first()
        
        if user:
            current_site = get_current_site(request)
            reset_url = reverse('password_reset_confirm', kwargs={'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                                                              'token': default_token_generator.make_token(user)})
            message = render_to_string('accounts/password_reset_email.html', {
                'user': user,
                'domain': current_site.domain,
                'protocol': 'https' if request.is_secure() else 'http',
                'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            send_mail(
                subject='Password Reset Request',
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
            messages.success(request, 'Password reset link sent to your email address')
            return redirect('login')
        
        messages.error(request, 'No account found with that email address')
    
    return render(request, 'accounts/password_reset.html')


def password_reset_confirm(request, uidb64, token):
    # Get user from uidb64 and token
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    # If request method is POST and new password and confirm password match, update password
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        # If passwords do not match, return to password reset form with error message
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return reverse('password_reset_confirm', kwargs={'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                                                              'token': default_token_generator.make_token(user)})
    
        if user and default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        
        messages.error(request, 'Password reset failed')
    
    # If user exists and token is valid, render password reset form
    if user is not None and default_token_generator.check_token(user, token):
        return render(request, 'accounts/password_reset_form.html', {'user': user})
    
    messages.error(request, 'Password reset link is invalid or expired')
    return redirect('password_reset')

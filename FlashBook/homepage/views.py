from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import RegisterForm, LoginForm
# Create your views here.

def homepage(request):
    return render(request,'homepage.html')


def about(request):
    return render(request,'about.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login') 
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


def login_views(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Logged in successfully!')

            if user.is_staff: 
                return redirect('/admin/')  
            else:  
                return redirect('homepage')  # จริง ๆ ต้องไปหน้า dashboard ของแต่ละ user
        """else:
            messages.error(request, 'Invalid username or password.')"""
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def logout_views(request):
    logout(request)
    messages.info(request, 'Logged out successfully!')
    return redirect('login')
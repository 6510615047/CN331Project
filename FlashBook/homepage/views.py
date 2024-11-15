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
            form.save()  # บันทึกผู้ใช้ลงฐานข้อมูล
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')  # เปลี่ยนไปหน้า Login หลังจากลงทะเบียนเสร็จ
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

            if user.is_staff:  # หากผู้ใช้เป็น Admin
                return redirect('/admin/')  # พาไปที่ Django Admin Panel
            else:  # หากเป็น User ทั่วไป
                return redirect('user_dashboard')  # เปลี่ยน 'home' เป็นชื่อ path ของหน้าแรก
        """else:
            messages.error(request, 'Invalid username or password.')"""
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def logout_views(request):
    logout(request)
    messages.info(request, 'Logged out successfully!')
    return redirect('login')

from django.contrib.auth.decorators import login_required

@login_required
def user_dashboard(request):
    return render(request, 'dashboard.html', {'user': request.user})
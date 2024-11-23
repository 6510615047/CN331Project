from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from homepage.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash

# Create your views here.

def homepage(request):
    return render(request, 'homepage.html')

def about(request):
    return render(request, 'about.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            newUser = User.objects.create(
                user=form.cleaned_data['username'],
                fname=form.cleaned_data['fname'],
                lname=form.cleaned_data['lname'],
                email=form.cleaned_data['email'],
            )
            newUser.set_password(form.cleaned_data['password1'])
            newUser.save()
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
                try:
                    # ดึงข้อมูลจากโมเดล User ของคุณโดยใช้ username
                    custom_user = User.objects.get(user=user.username)
                    request.session['user_id'] = custom_user.user_id
                except User.DoesNotExist:
                    messages.error(request, 'User not found in the database.')
                    return redirect('login')
                return redirect('/folder')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def logout_views(request):
    logout(request)
    messages.info(request, 'Logged out successfully!')
    return redirect('login')

@login_required
def profile_view(request):
    user_id = request.session.get('user_id')  # ดึง user_id จาก session ที่เก็บไว้ตอน login

    try:
        custom_user = User.objects.get(user_id=user_id)  # ดึงข้อมูลจากโมเดล User โดยใช้ user_id
        auth_user = request.user  # Django auth user
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('login')

    if request.method == 'POST':
        # รับข้อมูลใหม่จากผู้ใช้แล้วอัปเดต
        new_username = request.POST.get('user')
        new_fname = request.POST.get('fname')
        new_lname = request.POST.get('lname')
        new_email = request.POST.get('email')
        new_password = request.POST.get('password')

        # ตรวจสอบว่าชื่อผู้ใช้ใหม่ซ้ำหรือไม่
        if auth_user.username != new_username and User.objects.filter(user=new_username).exists():
            messages.error(request, 'Username already exists. Please choose a different one.')
            return redirect('profile')

        # อัปเดตข้อมูลใน custom User
        custom_user.user = new_username
        custom_user.fname = new_fname
        custom_user.lname = new_lname
        custom_user.email = new_email
        if 'profile_picture' in request.FILES:
            custom_user.profile_picture = request.FILES['profile_picture']
        custom_user.save()

        # อัปเดตข้อมูลใน auth User (Django default User model)
        auth_user.username = new_username
        auth_user.first_name = new_fname
        auth_user.last_name = new_lname
        auth_user.email = new_email
        if new_password:
            auth_user.set_password(new_password)  # เปลี่ยนรหัสผ่านและเข้ารหัส
        auth_user.save()

        # อัปเดต session authentication hash เพื่อให้ผู้ใช้ยังคงเข้าสู่ระบบอยู่หลังจากเปลี่ยนข้อมูล
        update_session_auth_hash(request, auth_user)

        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    context = {
        'user': custom_user,
    }
    return render(request, 'profile.html', context)

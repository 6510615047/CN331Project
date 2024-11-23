from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from homepage.models import User
from django.contrib.auth.decorators import login_required
#from folWordSel.views import folder_view
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
            newUser = User.objects.create(
                user = form.cleaned_data['username'],
                fname = form.cleaned_data['fname'],
                lname = form.cleaned_data['lname'],
                email = form.cleaned_data['email'],
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
                #request.session['user_id'] = User.objects.get(user=user).user_id
                #user = User.objects.get(user=user)
                # return folder_view(request) # จริง ๆ ต้องไปหน้า dashboard ของแต่ละ user
                try:
                    # ดึงข้อมูลจากโมเดล User ของคุณโดยใช้ username
                    custom_user = User.objects.get(user=user.username)
                    request.session['user_id'] = custom_user.user_id
                except User.DoesNotExist:
                    messages.error(request, 'User not found in the database.')
                    return redirect('login')
                return redirect('/folder')
        """else:
            messages.error(request, 'Invalid username or password.')"""
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
        auth_user = request.user
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('login')
    #user = request.user
    #custom_user = User.objects.get(user=user.username)  # ดึงข้อมูลจากโมเดล User
    #user = User.objects.get(user_id=request.session.get('user_id'))

    if request.method == 'POST':
        # รับข้อมูลใหม่จากผู้ใช้แล้วอัปเดต
        new_username = request.POST.get('user')
        custom_user.user = request.POST.get('user')
        custom_user.fname = request.POST.get('fname')
        custom_user.lname = request.POST.get('lname')
        custom_user.email = request.POST.get('email')
        custom_user.password = request.POST.get('password')
        if 'profile_picture' in request.FILES:
            custom_user.profile_picture = request.FILES['profile_picture']

        # อัปเดต username ทั้งในโมเดล custom User และ auth User
        if new_username != custom_user.user:
            custom_user.user = new_username
            auth_user.username = new_username  # อัปเดตชื่อผู้ใช้ในโมเดล auth User ด้วย

        custom_user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    context = {
        'user': custom_user,
    }
    return render(request, 'profile.html', context)

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile

def index(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        # In this project, we use email as username
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            try:
                profile = user.userprofile
                if profile.role == 'doctor':
                    return redirect('doctor')
                elif profile.role == 'lab':
                    return redirect('lab')
                elif profile.role == 'admin':
                    return redirect('admin_panel')
            except UserProfile.DoesNotExist:
                # Fallback if no profile exists
                return redirect('index')
        else:
            messages.error(request, "Invalid email or password")
            
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def doctor_view(request):
    if request.user.userprofile.role != 'doctor':
        return redirect('index')
    return render(request, 'doctor.html')

@login_required
def lab_view(request):
    if request.user.userprofile.role != 'lab':
        return redirect('index')
    return render(request, 'lab.html')

@login_required
def admin_view(request):
    if request.user.userprofile.role != 'admin':
        return redirect('index')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_user':
            name = request.POST.get('name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            role = request.POST.get('role')
            specialization = request.POST.get('specialization')
            
            if User.objects.filter(username=email).exists():
                messages.error(request, f"User with email {email} already exists.")
            else:
                user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
                UserProfile.objects.create(user=user, role=role, specialization=specialization)
                messages.success(request, f"Successfully added {role}: {name}")
                return redirect('admin_panel')

    # Get user lists
    doctors = User.objects.filter(userprofile__role='doctor')
    labs = User.objects.filter(userprofile__role='lab')
    
    context = {
        'doctors': doctors,
        'labs': labs,
        'doctor_count': doctors.count(),
        'lab_count': labs.count(),
        'total_users': User.objects.count()
    }
    
    return render(request, 'admin.html', context)

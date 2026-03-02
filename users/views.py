from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser


def home_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)
    return render(request, 'users/home.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect_by_role(user)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'users/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        role = request.POST.get('role', 'STUDENT')
        department = request.POST.get('department', '')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        else:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                role=role,
                department=department,
            )
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect_by_role(user)

    return render(request, 'users/register.html', {
        'roles': CustomUser.ROLE_CHOICES,
        'departments': CustomUser.DEPARTMENT_CHOICES,
    })


@login_required
def profile_view(request):
    return render(request, 'users/profile.html', {'user': request.user})


@login_required
def dashboard_view(request):
    return render(request, 'users/dashboard.html', {'user': request.user})


def redirect_by_role(user):
    from django.shortcuts import redirect
    role = getattr(user, 'role', 'STUDENT')
    if role == 'EVENT_COORDINATOR':
        return redirect('my_events')
    elif role == 'HOD':
        return redirect('hod_pending_events')
    elif role == 'PRINCIPAL':
        return redirect('principal_pending_events')
    else:
        return redirect('available_events')

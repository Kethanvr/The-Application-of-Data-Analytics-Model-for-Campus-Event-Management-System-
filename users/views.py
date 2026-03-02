from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import CustomUser
from .middleware import AnonymousUser


def _do_login(request, user):
    request.session['_auth_user_id'] = str(user.pk)
    request.session['_auth_user_backend'] = 'users.backends.MongoEngineBackend'
    request.session['_auth_user_hash'] = user.password[:20]
    request.session.save()


def _do_logout(request):
    request.session.flush()


def login_required_mongo(view_func):
    """Decorator equivalent to Django's @login_required for MongoEngine users."""
    from functools import wraps

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not getattr(request.user, 'is_authenticated', False):
            from django.conf import settings
            return redirect(settings.LOGIN_URL)
        return view_func(request, *args, **kwargs)

    return wrapper


def home_view(request):
    if getattr(request.user, 'is_authenticated', False):
        return redirect_by_role(request.user)
    return render(request, 'users/home.html')


def login_view(request):
    if getattr(request.user, 'is_authenticated', False):
        return redirect_by_role(request.user)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        from .backends import MongoEngineBackend
        backend = MongoEngineBackend()
        user = backend.authenticate(request, username=username, password=password)
        if user:
            _do_login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect_by_role(user)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'users/login.html')


def logout_view(request):
    _do_logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


def register_view(request):
    if getattr(request.user, 'is_authenticated', False):
        return redirect_by_role(request.user)

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        role = request.POST.get('role', 'STUDENT')
        department = request.POST.get('department', '') or None

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif CustomUser.objects(username=username).first():
            messages.error(request, 'Username already taken.')
        else:
            user = CustomUser.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                role=role,
                department=department,
            )
            _do_login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect_by_role(user)

    return render(request, 'users/register.html', {
        'roles': CustomUser.ROLE_CHOICES,
        'departments': CustomUser.DEPARTMENT_CHOICES,
    })


@login_required_mongo
def profile_view(request):
    return render(request, 'users/profile.html', {'user': request.user})


@login_required_mongo
def dashboard_view(request):
    return render(request, 'users/dashboard.html', {'user': request.user})


def redirect_by_role(user):
    role = getattr(user, 'role', 'STUDENT')
    if role == 'EVENT_COORDINATOR':
        return redirect('my_events')
    elif role == 'HOD':
        return redirect('hod_pending_events')
    elif role == 'PRINCIPAL':
        return redirect('principal_pending_events')
    else:
        return redirect('available_events')

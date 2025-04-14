from django.shortcuts import redirect
from django.urls import reverse
from functools import wraps

def patient_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.session.get('user_type') != 'patient':
            return redirect(reverse('access_denied'))
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def doctor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.session.get('user_type') != 'doctor':
            return redirect(reverse('access_denied'))
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.session.get('user_type') != 'admin':
            return redirect(reverse('access_denied'))
        return view_func(request, *args, **kwargs)
    return _wrapped_view
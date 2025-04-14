from django.shortcuts import redirect
from django.urls import reverse
import re

class UserTypeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Compile URL patterns that require specific user types
        self.patient_patterns = [
            re.compile(r'^/patient/'),
            re.compile(r'^/appointments/book/'),
        ]
        
        self.doctor_patterns = [
            re.compile(r'^/doctor/'),
            re.compile(r'^/prescriptions/create/'),
        ]
        
        self.admin_patterns = [
            re.compile(r'^/admin-portal/'),
        ]

    def __call__(self, request):
        # Skip middleware for authentication pages
        if request.path.startswith('/auth/') or request.path == '/' or request.path.startswith('/static/'):
            return self.get_response(request)
            
        # Check if user is logged in
        if 'user_type' not in request.session:
            if not request.path.startswith('/auth/'):
                return redirect(reverse('login'))
            return self.get_response(request)
        
        # Get user type from session
        user_type = request.session.get('user_type')
        
        # Check if patient is trying to access patient-only pages
        if any(pattern.match(request.path) for pattern in self.patient_patterns) and user_type != 'patient':
            return redirect(reverse('access_denied'))
            
        # Check if doctor is trying to access doctor-only pages
        if any(pattern.match(request.path) for pattern in self.doctor_patterns) and user_type != 'doctor':
            return redirect(reverse('access_denied'))
            
        # Check if admin is trying to access admin-only pages
        if any(pattern.match(request.path) for pattern in self.admin_patterns) and user_type != 'admin':
            return redirect(reverse('access_denied'))
            
        return self.get_response(request)
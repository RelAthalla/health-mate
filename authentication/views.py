from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection, IntegrityError
from django.views.decorators.http import require_http_methods
from .forms import LoginForm, PatientRegistrationForm
from core.utils import (
    authenticate_patient, authenticate_doctor, authenticate_admin,
    hash_password, dictfetchone
)
import requests
from django.conf import settings

@require_http_methods(["GET", "POST"])
def login_view(request):
    """User login view"""
    # Redirect if already logged in
    if 'user_type' in request.session:
        user_type = request.session['user_type']
        if user_type == 'patient':
            return redirect('patient_dashboard')
        elif user_type == 'doctor':
            return redirect('doctor_dashboard')
        elif user_type == 'admin':
            return redirect('admin_dashboard')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            password = form.cleaned_data['password']
            user_type = form.cleaned_data['user_type']
            
            recaptcha_response = request.POST.get('g-recaptcha-response')

            data = {
                'secret': settings.RECAPTCHA_SECRET_KEY, 
                'response': recaptcha_response
            }
            verify_url = 'https://www.google.com/recaptcha/api/siteverify'
            response = requests.post(verify_url, data=data)
            result = response.json()

            if not result.get('success'):
                messages.error(request, 'reCAPTCHA verification failed. Please try again.')

            user = None
            if user_type == 'patient':
                user = authenticate_patient(phone, password)
                if user:
                    request.session['user_type'] = 'patient'
                    request.session['user_id'] = user['patient_id']
                    request.session['user_name'] = user['name']
                    return redirect('patient_dashboard')
            elif user_type == 'doctor':
                user = authenticate_doctor(phone, password)
                if user:
                    request.session['user_type'] = 'doctor'
                    request.session['user_id'] = user['doctor_id']
                    request.session['user_name'] = user['name']
                    return redirect('doctor_dashboard')
            elif user_type == 'admin':
                user = authenticate_admin(phone, password)
                if user:
                    request.session['user_type'] = 'admin'
                    request.session['user_id'] = user['admin_id']
                    request.session['user_name'] = user['name']
                    return redirect('admin_dashboard')
            
            if not user:
                messages.error(request, 'Invalid phone number or password.')
    else:
        form = LoginForm()
    
    return render(request, 'authentication/login.html', {'form': form})

@require_http_methods(["GET", "POST"])
def patient_register(request):
    """Patient registration view"""
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            # Extract form data
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            full_name = f"{first_name} {last_name}"
            phone = form.cleaned_data['phone']
            sex = form.cleaned_data['sex']
            blood_type = form.cleaned_data['blood_type']
            birthdate = form.cleaned_data['birthdate']
            address = form.cleaned_data['address']
            password = hash_password(form.cleaned_data['password'])

            recaptcha_response = request.POST.get('g-recaptcha-response')

            data = {
                'secret': settings.RECAPTCHA_SECRET_KEY, 
                'response': recaptcha_response
            }
            verify_url = 'https://www.google.com/recaptcha/api/siteverify'
            response = requests.post(verify_url, data=data)
            result = response.json()

            if not result.get('success'):
                messages.error(request, 'reCAPTCHA verification failed. Please try again.')
                
            try:
                # Check if phone number already exists
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT patient_id FROM patient WHERE phone = %s",
                        [phone]
                    )
                    if dictfetchone(cursor):
                        messages.error(request, 'Phone number already registered.')
                        return render(request, 'authentication/patient_register.html', {'form': form})
                
                # Create new patient record
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO patient 
                        (first_name, last_name, name, sex, phone, blood_type, password, birthdate, address)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING patient_id
                        """,
                        [first_name, last_name, full_name, sex, phone, blood_type, password, birthdate, address]
                    )
                    new_patient_id = cursor.fetchone()[0]
                
                messages.success(request, 'Registration successful! Please log in.')
                return redirect('login')
                
            except IntegrityError as e:
                messages.error(request, f'Registration failed: {str(e)}')
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
    else:
        form = PatientRegistrationForm()
    
    return render(request, 'authentication/patient_register.html', {'form': form})

def logout_view(request):
    """Logout view"""
    # Clear all session data
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from utils.db_utils import execute_query

def patient_login(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        
        # Check patient credentials
        query = "SELECT * FROM patient WHERE phone = %s AND password = %s"
        patient = execute_query(query, (phone, password), fetch_one=True)
        
        if patient:
            # Create user session
            request.session['user_type'] = 'patient'
            request.session['user_id'] = patient[0]  # patient_id
            request.session['name'] = patient[3]     # name field
            return redirect('patient_dashboard')
        else:
            messages.error(request, 'Invalid phone number or password')
    
    return render(request, 'patient_login.html')

def doctor_login(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        
        # Check doctor credentials
        query = "SELECT * FROM doctor WHERE phone = %s AND password = %s"
        doctor = execute_query(query, (phone, password), fetch_one=True)
        
        if doctor:
            request.session['user_type'] = 'doctor'
            request.session['user_id'] = doctor[0]  # doctor_id
            request.session['name'] = doctor[3]     # name field
            return redirect('doctor_dashboard')
        else:
            messages.error(request, 'Invalid phone number or password')
    
    return render(request, 'doctor_login.html')

def admin_login(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        
        # Check admin credentials
        query = "SELECT * FROM admin WHERE phone = %s AND password = %s"
        admin = execute_query(query, (phone, password), fetch_one=True)
        
        if admin:
            request.session['user_type'] = 'admin'
            request.session['user_id'] = admin[0]  # admin_id
            request.session['name'] = admin[3]     # name field
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid phone number or password')
    
    return render(request, 'admin_login.html')

def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('home')
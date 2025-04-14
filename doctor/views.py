from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import connection
from datetime import datetime
from core.decorators import doctor_required
from core.utils import (
    get_doctor, get_doctor_appointments, get_patient,
    create_prescription, dictfetchall, dictfetchone
)

@doctor_required
def dashboard(request):
    """Doctor dashboard view"""
    doctor_id = request.session.get('user_id')
    
    # Get doctor data
    doctor = get_doctor(doctor_id)
    
    # Get upcoming appointments
    appointments = get_doctor_appointments(doctor_id)
    today = datetime.now().date()
    upcoming_appointments = [a for a in appointments if datetime.strptime(a['date'].strftime('%Y-%m-%d'), '%Y-%m-%d').date() >= today][:5]
    
    # Get appointment counts
    today_count = len([a for a in appointments if a['date'] == today])
    total_count = len(appointments)
    
    context = {
        'doctor': doctor,
        'upcoming_appointments': upcoming_appointments,
        'today_count': today_count,
        'total_count': total_count
    }
    
    return render(request, 'doctor/dashboard.html', context)

@doctor_required
def profile(request):
    """Doctor profile view"""
    doctor_id = request.session.get('user_id')
    doctor = get_doctor(doctor_id)
    
    if request.method == 'POST':
        # Extract form data
        data = {
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'name': f"{request.POST.get('first_name')} {request.POST.get('last_name')}",
            'phone': request.POST.get('phone'),
            'sex': request.POST.get('sex'),
            'specialization': request.POST.get('specialization'),
            'experience': request.POST.get('experience'),
            'birthdate': request.POST.get('birthdate'),
            'address': request.POST.get('address')
        }
        
        # Update doctor record
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE doctor SET 
                first_name = %s, last_name = %s, name = %s, phone = %s, 
                sex = %s, specialization = %s, experience = %s, 
                birthdate = %s, address = %s
                WHERE doctor_id = %s
                """,
                [
                    data['first_name'], data['last_name'], data['name'], data['phone'],
                    data['sex'], data['specialization'], data['experience'],
                    data['birthdate'], data['address'], doctor_id
                ]
            )
            
        # Update session name if changed
        request.session['user_name'] = data['name']
        messages.success(request, 'Profile updated successfully.')
        
        # Fetch updated doctor data
        doctor = get_doctor(doctor_id)
    
    return render(request, 'doctor/profile.html', {'doctor': doctor})

@doctor_required
def appointments(request):
    """Doctor appointments view"""
    doctor_id = request.session.get('user_id')
    
    # Get all appointments
    appointments = get_doctor_appointments(doctor_id)
    
    # Separate upcoming and past appointments
    upcoming = []
    past = []
    today = datetime.now().date()
    
    for appointment in appointments:
        appointment_date = datetime.strptime(appointment['date'].strftime('%Y-%m-%d'), '%Y-%m-%d').date()
        if appointment_date >= today:
            upcoming.append(appointment)
        else:
            past.append(appointment)
    
    context = {
        'upcoming_appointments': upcoming,
        'past_appointments': past
    }
    
    return render(request, 'doctor/appointments.html', context)

@doctor_required
def patients(request):
    """View doctor's patients"""
    doctor_id = request.session.get('user_id')
    
    # Get all patients who had appointments with this doctor
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT p.patient_id, p.name, p.phone, p.sex, p.blood_type
            FROM appointment a
            JOIN patient p ON a.patient_id = p.patient_id
            WHERE a.doctor_id = %s
            ORDER BY p.name
            """,
            [doctor_id]
        )
        patients = dictfetchall(cursor)
    
    return render(request, 'doctor/patients.html', {'patients': patients})

@doctor_required
def patient_detail(request, patient_id):
    """View patient details"""
    doctor_id = request.session.get('user_id')
    
    # Check if this doctor has appointments with this patient
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*) as count
            FROM appointment
            WHERE doctor_id = %s AND patient_id = %s
            """,
            [doctor_id, patient_id]
        )
        result = dictfetchone(cursor)
        
        if not result or result['count'] == 0:
            messages.error(request, "You don't have permission to view this patient.")
            return redirect('doctor_patients')
    
    # Get patient data
    patient = get_patient(patient_id)
    
    # Get appointment history
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT *
            FROM appointment
            WHERE doctor_id = %s AND patient_id = %s
            ORDER BY date DESC, time DESC
            """,
            [doctor_id, patient_id]
        )
        appointments = dictfetchall(cursor)
    
    # Get prescriptions
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT *
            FROM prescription
            WHERE patient_id = %s
            ORDER BY prescription_id DESC
            """,
            [patient_id]
        )
        prescriptions = dictfetchall(cursor)
    
    context = {
        'patient': patient,
        'appointments': appointments,
        'prescriptions': prescriptions
    }
    
    return render(request, 'doctor/patient_detail.html', context)

@doctor_required
def create_prescription_view(request, patient_id):
    """Create prescription view"""
    doctor_id = request.session.get('user_id')
    
    # Check if this doctor has appointments with this patient
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*) as count
            FROM appointment
            WHERE doctor_id = %s AND patient_id = %s
            """,
            [doctor_id, patient_id]
        )
        result = dictfetchone(cursor)
        
        if not result or result['count'] == 0:
            messages.error(request, "You don't have permission to create prescriptions for this patient.")
            return redirect('doctor_patients')
    
    # Get patient data
    patient = get_patient(patient_id)
    
    if request.method == 'POST':
        medicine = request.POST.get('medicine')
        advice = request.POST.get('advice')
        
        if not medicine or not advice:
            messages.error(request, "Please fill in all fields.")
        else:
            # Create prescription
            prescription_id = create_prescription(patient_id, medicine, advice)
            
            if prescription_id:
                messages.success(request, "Prescription created successfully.")
                return redirect('doctor_patient_detail', patient_id=patient_id)
            else:
                messages.error(request, "Failed to create prescription.")
    
    return render(request, 'doctor/create_prescription.html', {'patient': patient})

@doctor_required
def schedule(request):
    """Doctor's schedule view"""
    doctor_id = request.session.get('user_id')
    
    # Get appointments for the next 7 days
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT a.*, p.name as patient_name
            FROM appointment a
            JOIN patient p ON a.patient_id = p.patient_id
            WHERE a.doctor_id = %s AND a.date BETWEEN CURRENT_DATE AND (CURRENT_DATE + INTERVAL '7 days')
            ORDER BY a.date, a.time
            """,
            [doctor_id]
        )
        upcoming_appointments = dictfetchall(cursor)
    
    # Group appointments by date
    schedule = {}
    for appointment in upcoming_appointments:
        date_str = appointment['date'].strftime('%Y-%m-%d')
        if date_str not in schedule:
            schedule[date_str] = []
        schedule[date_str].append(appointment)
    
    return render(request, 'doctor/schedule.html', {'schedule': schedule})
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from core.decorators import admin_required
from core.utils import (
    get_admin, get_all_doctors, get_patient,
    dictfetchall, dictfetchone, hash_password
)

@admin_required
def dashboard(request):
    """Admin dashboard view"""
    admin_id = request.session.get('user_id')
    
    # Get admin data
    admin = get_admin(admin_id)
    
    # Get counts
    with connection.cursor() as cursor:
        # Count patients
        cursor.execute("SELECT COUNT(*) as count FROM patient")
        patient_count = dictfetchone(cursor)['count']
        
        # Count doctors
        cursor.execute("SELECT COUNT(*) as count FROM doctor")
        doctor_count = dictfetchone(cursor)['count']
        
        # Count appointments
        cursor.execute("SELECT COUNT(*) as count FROM appointment")
        appointment_count = dictfetchone(cursor)['count']
        
        # Count prescriptions
        cursor.execute("SELECT COUNT(*) as count FROM prescription")
        prescription_count = dictfetchone(cursor)['count']
        
        # Count bills
        cursor.execute("SELECT COUNT(*) as count FROM bill")
        bill_count = dictfetchone(cursor)['count']
        
        # Get total revenue
        cursor.execute("SELECT COALESCE(SUM(amount), 0) as total FROM bill")
        total_revenue = dictfetchone(cursor)['total']
    
    context = {
        'admin': admin,
        'patient_count': patient_count,
        'doctor_count': doctor_count,
        'appointment_count': appointment_count,
        'prescription_count': prescription_count,
        'bill_count': bill_count,
        'total_revenue': total_revenue
    }
    
    return render(request, 'admin_portal/dashboard.html', context)

@admin_required
def manage_patients(request):
    """Manage patients view"""
    # Get all patients
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM patient ORDER BY name")
        patients = dictfetchall(cursor)
    
    return render(request, 'admin_portal/manage_patients.html', {'patients': patients})

@admin_required
def patient_detail(request, patient_id):
    """View patient details"""
    # Get patient data
    patient = get_patient(patient_id)
    
    if not patient:
        messages.error(request, "Patient not found.")
        return redirect('manage_patients')
    
    # Get appointment history
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT a.*, d.First_Name || ' ' || d.Last_Name AS doctor_name
            FROM appointment a
            JOIN doctor d ON a.doctor_id = d.doctor_id
            WHERE a.patient_id = %s
            ORDER BY a.date DESC, a.time DESC
            """,
            [patient_id]
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
    
    # Get bills
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT *
            FROM bill
            WHERE patient_id = %s
            ORDER BY date DESC, time DESC
            """,
            [patient_id]
        )
        bills = dictfetchall(cursor)
    
    context = {
        'patient': patient,
        'appointments': appointments,
        'prescriptions': prescriptions,
        'bills': bills
    }
    
    return render(request, 'admin_portal/patient_detail.html', context)

@admin_required
def manage_doctors(request):
    """Manage doctors view"""
    # Get all doctors
    doctors = get_all_doctors()
    
    return render(request, 'admin_portal/manage_doctors.html', {'doctors': doctors})

@admin_required
def doctor_detail(request, doctor_id):
    """View doctor details"""
    # Get doctor data
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM doctor WHERE doctor_id = %s",
            [doctor_id]
        )
        doctor = dictfetchone(cursor)
    
    if not doctor:
        messages.error(request, "Doctor not found.")
        return redirect('manage_doctors')
    
    # Get appointment history
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT a.*, p.name as patient_name
            FROM appointment a
            JOIN patient p ON a.patient_id = p.patient_id
            WHERE a.doctor_id = %s
            ORDER BY a.date DESC, a.time DESC
            """,
            [doctor_id]
        )
        appointments = dictfetchall(cursor)
    
    context = {
        'doctor': doctor,
        'appointments': appointments
    }
    
    return render(request, 'admin_portal/doctor_detail.html', context)

@admin_required
def add_doctor(request):
    """Add new doctor view"""
    if request.method == 'POST':
        # Extract form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        full_name = f"{first_name} {last_name}"
        phone = request.POST.get('phone')
        sex = request.POST.get('sex')
        specialization = request.POST.get('specialization')
        experience = request.POST.get('experience')
        birthdate = request.POST.get('birthdate')
        address = request.POST.get('address')
        password = hash_password(request.POST.get('password'))
        
        # Validate data
        if not all([first_name, last_name, phone, sex, specialization, experience, birthdate, address, password]):
            messages.error(request, "Please fill in all fields.")
            return render(request, 'admin_portal/add_doctor.html')
        
        try:
            # Check if phone number already exists
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT doctor_id FROM doctor WHERE phone = %s",
                    [phone]
                )
                if dictfetchone(cursor):
                    messages.error(request, 'Phone number already registered.')
                    return render(request, 'admin_portal/add_doctor.html')
            
            # Create new doctor record
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO doctor 
                    (first_name, last_name, name, sex, phone, specialization, password, birthdate, address, experience)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING doctor_id
                    """,
                    [first_name, last_name, full_name, sex, phone, specialization, password, birthdate, address, experience]
                )
                new_doctor_id = cursor.fetchone()[0]
            
            messages.success(request, f'Doctor {full_name} added successfully.')
            return redirect('manage_doctors')
            
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    
    return render(request, 'admin_portal/add_doctor.html')

@admin_required
def appointments(request):
    """View all appointments"""
    # Get all appointments
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT a.*, p.name as patient_name, d.First_Name || ' ' || d.Last_Name AS doctor_name
            FROM appointment a
            JOIN patient p ON a.patient_id = p.patient_id
            JOIN doctor d ON a.doctor_id = d.doctor_id
            ORDER BY a.date DESC, a.time DESC
            """
        )
        appointments = dictfetchall(cursor)
    
    return render(request, 'admin_portal/appointments.html', {'appointments': appointments})

@admin_required
def prescriptions(request):
    """View all prescriptions"""
    # Get all prescriptions
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT pr.*, p.name as patient_name
            FROM prescription pr
            JOIN patient p ON pr.patient_id = p.patient_id
            ORDER BY pr.prescription_id DESC
            """
        )
        prescriptions = dictfetchall(cursor)
    
    return render(request, 'admin_portal/prescriptions.html', {'prescriptions': prescriptions})

@admin_required
def bills(request):
    """View all bills"""
    # Get all bills
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT b.*, p.name as patient_name
            FROM bill b
            JOIN patient p ON b.patient_id = p.patient_id
            ORDER BY b.date DESC, b.time DESC
            """
        )
        bills = dictfetchall(cursor)
    
    return render(request, 'admin_portal/bills.html', {'bills': bills})

@admin_required
def statistics(request):
    """View system statistics"""
    with connection.cursor() as cursor:
        # Get patient registration stats by month
        cursor.execute(
            """
            SELECT 
                EXTRACT(YEAR FROM birthdate) as year,
                EXTRACT(MONTH FROM birthdate) as month,
                COUNT(*) as count
            FROM 
                patient
            GROUP BY 
                EXTRACT(YEAR FROM birthdate),
                EXTRACT(MONTH FROM birthdate)
            ORDER BY 
                year, month
            """
        )
        patient_stats = dictfetchall(cursor)
        
        # Get appointment stats by specialization
        cursor.execute(
            """
            SELECT 
                specialization,
                COUNT(*) as count
            FROM 
                appointment
            GROUP BY 
                specialization
            ORDER BY 
                count DESC
            """
        )
        appointment_stats = dictfetchall(cursor)
        
        # Get revenue stats by month
        cursor.execute(
            """
            SELECT 
                EXTRACT(YEAR FROM date) as year,
                EXTRACT(MONTH FROM date) as month,
                SUM(amount) as total
            FROM 
                bill
            GROUP BY 
                EXTRACT(YEAR FROM date),
                EXTRACT(MONTH FROM date)
            ORDER BY 
                year, month
            """
        )
        revenue_stats = dictfetchall(cursor)
    
    context = {
        'patient_stats': patient_stats,
        'appointment_stats': appointment_stats,
        'revenue_stats': revenue_stats
    }
    
    return render(request, 'admin_portal/statistics.html', context)
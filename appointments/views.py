from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import connection
from django.http import JsonResponse
from datetime import datetime, timedelta, time
from core.decorators import patient_required
from core.utils import (
    get_doctor, get_all_doctors, create_appointment,
    dictfetchall, dictfetchone
)
from .forms import AppointmentForm

@patient_required
def book_appointment(request, doctor_id=None):
    """Book appointment view"""
    patient_id = request.session.get('user_id')
    
    # If doctor_id is not provided, show doctor selection page
    if not doctor_id:
        doctors = get_all_doctors()
        return render(request, 'appointments/select_doctor.html', {'doctors': doctors})
    
    # Get doctor data
    doctor = get_doctor(doctor_id)
    
    if not doctor:
        messages.error(request, "Doctor not found.")
        return redirect('find_doctors')
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            time_str = form.cleaned_data['time']
            
            # Convert time string to time object
            appointment_time = datetime.strptime(time_str, '%H:%M').time()
            
            # Check if the appointment slot is available
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*) as count
                    FROM appointment
                    WHERE doctor_id = %s AND date = %s AND time = %s
                    """,
                    [doctor_id, date, appointment_time]
                )
                result = dictfetchone(cursor)
                
                if result['count'] > 0:
                    messages.error(request, "This time slot is already booked. Please select another time.")
                    return redirect('book_appointment', doctor_id=doctor_id)
            
            # Create appointment
            appointment_id = create_appointment(patient_id, doctor_id, date, appointment_time)
            
            if appointment_id:
                # Create bill for the appointment
                appointment_fee = 100000.00  # Example fee
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO bill 
                        (patient_id, date, time, amount)
                        VALUES (%s, %s, %s, %s)
                        """,
                        [patient_id, datetime.now().date(), datetime.now().time(), appointment_fee]
                    )
                
                messages.success(request, "Appointment booked successfully.")
                return redirect('patient_appointments')
            else:
                messages.error(request, "Failed to book appointment.")
    else:
        # Get available time slots
        available_times = get_available_time_slots(doctor_id, datetime.now().date())
        form = AppointmentForm(available_times=available_times)
    
    context = {
        'doctor': doctor,
        'form': form
    }
    
    return render(request, 'appointments/book_appointment.html', context)

def get_available_time_slots(doctor_id, date):
    """Get available time slots for a doctor on a specific date"""
    # Define working hours (9 AM to 5 PM)
    working_hours_start = time(9, 0)
    working_hours_end = time(17, 0)
    
    # Generate all possible time slots (every 30 minutes)
    all_slots = []
    current_time = datetime.combine(datetime.today(), working_hours_start)
    end_time = datetime.combine(datetime.today(), working_hours_end)
    
    while current_time <= end_time:
        all_slots.append(current_time.time())
        current_time += timedelta(minutes=30)
    
    # Get booked slots
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT time
            FROM appointment
            WHERE doctor_id = %s AND date = %s
            """,
            [doctor_id, date]
        )
        booked_slots = [row[0] for row in cursor.fetchall()]
    
    # Filter out booked slots
    available_slots = [slot for slot in all_slots if slot not in booked_slots]
    
    return available_slots

def get_available_slots_api(request):
    """API endpoint to get available time slots"""
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')
    
    if not doctor_id or not date_str:
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    
    available_slots = get_available_time_slots(doctor_id, date)
    slots_formatted = [slot.strftime('%H:%M') for slot in available_slots]
    
    return JsonResponse({'available_slots': slots_formatted})

@patient_required
def cancel_appointment(request, appointment_id):
    """Cancel appointment view"""
    patient_id = request.session.get('user_id')
    
    # Check if the appointment belongs to this patient
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT *
            FROM appointment
            WHERE appointment_id = %s AND patient_id = %s
            """,
            [appointment_id, patient_id]
        )
        appointment = dictfetchone(cursor)
    
    if not appointment:
        messages.error(request, "Appointment not found or you don't have permission to cancel it.")
        return redirect('patient_appointments')
    
    # Check if the appointment is in the future
    appointment_date = appointment['date']
    current_date = datetime.now().date()
    
    if appointment_date < current_date:
        messages.error(request, "Cannot cancel past appointments.")
        return redirect('patient_appointments')
    
    # Cancel the appointment
    with connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM appointment
            WHERE appointment_id = %s
            """,
            [appointment_id]
        )
    
    messages.success(request, "Appointment cancelled successfully.")
    return redirect('patient_appointments')

@patient_required
def reschedule_appointment(request, appointment_id):
    """Reschedule appointment view"""
    patient_id = request.session.get('user_id')
    
    # Check if the appointment belongs to this patient
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT a.*, d.doctor_id
            FROM appointment a
            JOIN doctor d ON a.doctor_id = d.doctor_id
            WHERE a.appointment_id = %s AND a.patient_id = %s
            """,
            [appointment_id, patient_id]
        )
        appointment = dictfetchone(cursor)
    
    if not appointment:
        messages.error(request, "Appointment not found or you don't have permission to reschedule it.")
        return redirect('patient_appointments')
    
    # Check if the appointment is in the future
    appointment_date = appointment['date']
    current_date = datetime.now().date()
    
    if appointment_date < current_date:
        messages.error(request, "Cannot reschedule past appointments.")
        return redirect('patient_appointments')
    
    doctor_id = appointment['doctor_id']
    doctor = get_doctor(doctor_id)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            time_str = form.cleaned_data['time']
            
            # Convert time string to time object
            appointment_time = datetime.strptime(time_str, '%H:%M').time()
            
            # Check if the appointment slot is available
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*) as count
                    FROM appointment
                    WHERE doctor_id = %s AND date = %s AND time = %s AND appointment_id != %s
                    """,
                    [doctor_id, date, appointment_time, appointment_id]
                )
                result = dictfetchone(cursor)
                
                if result['count'] > 0:
                    messages.error(request, "This time slot is already booked. Please select another time.")
                    return redirect('reschedule_appointment', appointment_id=appointment_id)
            
            # Update appointment
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE appointment
                    SET date = %s, time = %s
                    WHERE appointment_id = %s
                    """,
                    [date, appointment_time, appointment_id]
                )
            
            messages.success(request, "Appointment rescheduled successfully.")
            return redirect('patient_appointments')
    else:
        # Get available time slots
        available_times = get_available_time_slots(doctor_id, datetime.now().date())
        
        # Add current appointment time to available times
        current_time = appointment['time']
        if current_time not in available_times:
            available_times.append(current_time)
            available_times.sort()
        
        # Pre-populate form with current appointment date and time
        initial_data = {
            'date': appointment['date'],
            'time': appointment['time'].strftime('%H:%M')
        }
        
        form = AppointmentForm(initial=initial_data, available_times=available_times)
    
    context = {
        'doctor': doctor,
        'form': form,
        'appointment': appointment,
        'is_reschedule': True
    }
    
    return render(request, 'appointments/book_appointment.html', context)
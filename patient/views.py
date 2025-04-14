from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from datetime import datetime
from core.decorators import patient_required
from core.utils import (
    get_patient, update_patient, get_patient_appointments,
    get_patient_prescriptions, get_patient_bills,
    update_wallet_balance, get_all_doctors, get_doctors_by_specialization,
    hash_password, dictfetchone, get_patient_bills_paid, get_patient_bills_topup, get_patient_bills_topup_or_paid
)
from .forms import PatientProfileForm, WalletPinForm, WalletTopUpForm
import firebase_admin
from firebase_admin import credentials, auth
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST

@patient_required
def dashboard(request):
    """Patient dashboard view"""
    patient_id = request.session.get('user_id')
    user_type = request.session.get('user_type')
    
    # Get patient data
    patient = get_patient(patient_id)
    
    # Get upcoming appointments
    appointments = get_patient_appointments(patient_id)
    upcoming_appointments = [a for a in appointments if 
                            datetime.strptime(a['date'].strftime('%Y-%m-%d'), '%Y-%m-%d').date() >= datetime.now().date()][:3]
    
    # Get recent prescriptions
    prescriptions = get_patient_prescriptions(patient_id)[:3]
    
    # Get recent bills
    bills = get_patient_bills(patient_id)[:3]
    
    context = {
        'patient': patient,
        'upcoming_appointments': upcoming_appointments,
        'prescriptions': prescriptions,
        'bills': bills, 
        'user_type': user_type
        
    }
    
    return render(request, 'patient/dashboard.html', context)

@patient_required
def profile(request):
    """Patient profile view"""
    patient_id = request.session.get('user_id')
    patient = get_patient(patient_id)
    
    if request.method == 'POST':
        form = PatientProfileForm(request.POST)
        if form.is_valid():
            # Extract form data
            data = {
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'name': f"{form.cleaned_data['first_name']} {form.cleaned_data['last_name']}",
                'phone': form.cleaned_data['phone'],
                'sex': form.cleaned_data['sex'],
                'blood_type': form.cleaned_data['blood_type'],
                'birthdate': form.cleaned_data['birthdate'],
                'address': form.cleaned_data['address']
            }
            
            # Update patient record
            if update_patient(patient_id, data):
                # Update session name if changed
                request.session['user_name'] = data['name']
                messages.success(request, 'Profile updated successfully.')
                return redirect('patient_profile')
            else:
                messages.error(request, 'Failed to update profile.')
    else:
        # Prepopulate form with patient data
        form = PatientProfileForm(initial={
            'first_name': patient['first_name'],
            'last_name': patient['last_name'],
            'phone': patient['phone'],
            'sex': patient['sex'],
            'blood_type': patient['blood_type'],
            'birthdate': patient['birthdate'],
            'address': patient['address']
        })
    
    return render(request, 'patient/profile.html', {'form': form, 'patient': patient})

    
@patient_required
def request_otp(request):
    """View to request phone verification"""
    patient_id = request.session.get('user_id')
    
    # Get patient's phone number from database
    phone_number = get_patient_phone(patient_id)
    
    if not phone_number:
        messages.error(request, "Phone number not found for your account.")
        return redirect('profile_update')
    
    # Format phone number in E.164 format for Firebase
    # Adjust this based on your data format and country code
    formatted_phone = "+62" + phone_number[1:] if phone_number.startswith("08") else phone_number
    
    # Store phone number in session for verification
    request.session['verification_phone'] = formatted_phone
    
    context = {
        'phone_number': phone_number[-4:],  # Only show last 4 digits
        'full_phone_number': formatted_phone,
        'firebase_config': settings.FIREBASE_CONFIG
    }
    
    return render(request, 'patient/request_otp.html', context)

@require_POST
def verify_firebase_token(request):
    """API endpoint to verify Firebase ID token"""
    id_token = request.POST.get('idToken')
    
    if not id_token:
        return JsonResponse({'success': False, 'error': 'No token provided'})
    
    try:
        # Verify the ID token
        decoded_token = auth.verify_id_token(id_token)
        
        # Check if phone number matches
        firebase_phone = decoded_token.get('phone_number')
        session_phone = request.session.get('verification_phone')
        
        if firebase_phone == session_phone:
            # Mark as verified in session
            request.session['otp_verified'] = True
            # Store verification timestamp
            request.session['otp_verified_at'] = datetime.now().timestamp()
            # Clean up session
            if 'verification_phone' in request.session:
                del request.session['verification_phone']
            
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Phone number mismatch'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@patient_required
def appointments(request):
    """Patient appointments view"""
    patient_id = request.session.get('user_id')
    user_type = request.session.get('user_type')
    
    # Check if OTP is verified
    if not request.session.get('otp_verified'):
        return redirect('request_otp')
    
    # Optional: Check if OTP verification has expired (e.g., after 24 hours)
    verified_at = request.session.get('otp_verified_at')
    current_time = datetime.now().timestamp()
    verification_ttl = 86400  # 24 hours in seconds
    
    if verified_at and (current_time - verified_at > verification_ttl):
        # Verification expired
        request.session['otp_verified'] = False
        if 'otp_verified_at' in request.session:
            del request.session['otp_verified_at']
        messages.info(request, "Your verification has expired. Please verify again.")
        return redirect('request_otp')
    
    # Get all appointments
    appointments = get_patient_appointments(patient_id)
    
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
        'past_appointments': past,
        'user_type': user_type
    }
    
    return render(request, 'patient/appointments.html', context)

@patient_required
def find_doctors(request):
    """Find doctors view"""
    specialization = request.GET.get('specialization', None)
    user_type = request.session.get('user_type')
    
    doctors = get_all_doctors()
    
    # Get all unique specializations for filter dropdown
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT specialization FROM doctor ORDER BY specialization")
        specializations = [row[0] for row in cursor.fetchall()]
    
    context = {
        'doctors': doctors,
        'specializations': specializations,
        'selected_specialization': specialization,
        'user_type': user_type
    }
    
    return render(request, 'patient/find_doctors.html', context)

@patient_required
def prescriptions(request):
    """Patient prescriptions view"""
    patient_id = request.session.get('user_id')
    
    # Get all prescriptions
    prescriptions = get_patient_prescriptions(patient_id)
    
    return render(request, 'patient/prescriptions.html', {
        'prescriptions': prescriptions
    })

@patient_required
def medical_history(request):
    """Patient medical history view"""
    patient_id = request.session.get('user_id')
    user_type = request.session.get('user_type')
    
    # Get patient data
    patient = get_patient(patient_id)
    
    # Get all appointments
    appointments = get_patient_appointments(patient_id)
    
    # Get all prescriptions
    prescriptions = get_patient_prescriptions(patient_id)
    
    context = {
        'patient': patient,
        'appointments': appointments,
        'prescriptions': prescriptions,
        'user_type': user_type
    }
    
    return render(request, 'patient/medical_history.html', context)

@patient_required
def wallet(request):
    """Patient wallet view"""
    patient_id = request.session.get('user_id')
    
    patient = get_patient(patient_id)
    
    # Get recent bills/transactions
    transactions = get_patient_bills_topup_or_paid(patient_id)[:5]
    transactions = transactions[::-1]
    
    context = {
        'wallet_balance': patient['wallet_balance'],
        'transactions': transactions,
    }
    
    return render(request, 'patient/wallet.html', context)

@patient_required
def update_wallet_pin(request):
    """Update wallet PIN view"""
    patient_id = request.session.get('user_id')
    
    if request.method == 'POST':
        form = WalletPinForm(request.POST)
        if form.is_valid():
            current_pin = form.cleaned_data['current_pin']
            new_pin = form.cleaned_data['new_pin']
            
            # Verify current PIN
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT patient_id FROM patient WHERE patient_id = %s AND wallet_pin = %s",
                    [patient_id, current_pin]
                )
                if not dictfetchone(cursor):
                    messages.error(request, 'Current PIN is incorrect.')
                    return render(request, 'patient/update_wallet_pin.html', {'form': form})
                
                # Update PIN
                cursor.execute(
                    "UPDATE patient SET wallet_pin = %s WHERE patient_id = %s",
                    [new_pin, patient_id]
                )
                
                messages.success(request, 'Wallet PIN updated successfully.')
                return redirect('patient_wallet')
    else:
        form = WalletPinForm()
    
    return render(request, 'patient/update_wallet_pin.html', {'form': form})

@patient_required
def topup_wallet(request):
    """Top up wallet view"""
    patient_id = request.session.get('user_id')
    patient = get_patient(patient_id)
    
    if request.method == 'POST':
        form = WalletTopUpForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            pin = form.cleaned_data['pin']
            
            # Process top-up
            if update_wallet_balance(patient_id, amount, pin):
                # Create bill record for the top-up
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO bill 
                        (patient_id, date, time, amount, status)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        [patient_id, datetime.now().date(), datetime.now().time(), amount, "Topup"]
                    )
                
                messages.success(request, f'Successfully added {amount} to your wallet.')
                return redirect('patient_wallet')
            else:
                messages.error(request, 'Failed to top up wallet. Please check your PIN.')
    else:
        form = WalletTopUpForm()
    
    return render(request, 'patient/topup_wallet.html', {'form': form, 'patient': patient})
    
@patient_required
def bills(request):
    """Patient bills view"""
    patient_id = request.session.get('user_id')
    
    # Get all bills
    bills = get_patient_bills(patient_id)
    
    return render(request, 'patient/bills.html', {
        'bills': bills
    })
    
def bills_paid(request):
    """Patient bills view"""
    patient_id = request.session.get('user_id')
    
    # Get all bills
    bills_paid = get_patient_bills_paid(patient_id)
    topup = get_patient_bills_topup(patient_id)
    
    return render(request, 'patient/bills_paid.html', {
        'bills_paid': bills_paid,
        'topup': topup
    })
    
@patient_required
def invoice(request, bill_id):
    """View invoice details"""
    patient_id = request.session.get('user_id')
    
    # Check if bill exists and belongs to this patient
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT b.*, p.name as patient_name FROM bill b JOIN patient p ON b.patient_id = p.patient_id WHERE b.bill_id = %s AND b.patient_id = %s",
            [bill_id, patient_id]
        )
        bill = dictfetchone(cursor)
    
    if not bill:
        messages.error(request, "Invoice not found or you don't have permission to view it.")
        return redirect('payment_history')
    
    return render(request, 'patient/invoice.html', {'bill': bill})
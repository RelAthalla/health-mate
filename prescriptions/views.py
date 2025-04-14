from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import connection
from django.http import HttpResponse
from datetime import datetime
from core.decorators import patient_required, doctor_required
from core.utils import (
    dictfetchone, create_prescription
)

@patient_required
def view_prescription(request, prescription_id):
    """View prescription details"""
    patient_id = request.session.get('user_id')
    
    # Check if the prescription belongs to this patient
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT p.*, pat.name as patient_name
            FROM prescription p
            JOIN patient pat ON p.patient_id = pat.patient_id
            WHERE p.prescription_id = %s AND p.patient_id = %s
            """,
            [prescription_id, patient_id]
        )
        prescription = dictfetchone(cursor)
    
    if not prescription:
        messages.error(request, "Prescription not found or you don't have permission to view it.")
        return redirect('patient_prescriptions')
    
    return render(request, 'prescriptions/view_prescription.html', {'prescription': prescription})

@doctor_required
def create_prescription_view(request):
    """Create prescription view"""
    doctor_id = request.session.get('user_id')
    
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        medicine = request.POST.get('medicine')
        advice = request.POST.get('advice')
        
        if not all([patient_id, medicine, advice]):
            messages.error(request, "Please fill in all fields.")
            return redirect('doctor_patients')
        
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
        
        # Create prescription
        prescription_id = create_prescription(patient_id, medicine, advice)
        
        if prescription_id:
            messages.success(request, "Prescription created successfully.")
            return redirect('doctor_patient_detail', patient_id=patient_id)
        else:
            messages.error(request, "Failed to create prescription.")
    
    # Get patients this doctor has appointments with
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT p.patient_id, p.name
            FROM appointment a
            JOIN patient p ON a.patient_id = p.patient_id
            WHERE a.doctor_id = %s
            ORDER BY p.name
            """,
            [doctor_id]
        )
        patients = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
    
    return render(request, 'prescriptions/create_prescription.html', {'patients': patients})

@patient_required
def download_prescription(request, prescription_id):
    """Download prescription as PDF (simplified version - just returns HTML)"""
    patient_id = request.session.get('user_id')
    
    # Check if the prescription belongs to this patient
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT p.*, pat.name as patient_name, pat.address, pat.birthdate, pat.sex
            FROM prescription p
            JOIN patient pat ON p.patient_id = pat.patient_id
            WHERE p.prescription_id = %s AND p.patient_id = %s
            """,
            [prescription_id, patient_id]
        )
        prescription = dictfetchone(cursor)
    
    if not prescription:
        messages.error(request, "Prescription not found or you don't have permission to view it.")
        return redirect('patient_prescriptions')
    
    # In a real application, you would generate a PDF here
    # For simplicity, we just render a printable HTML page
    
    return render(request, 'prescriptions/download_prescription.html', {'prescription': prescription})
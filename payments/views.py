from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from datetime import datetime
from core.decorators import patient_required
from core.utils import (
    get_patient, get_patient_bills, pay_from_wallet,
    update_wallet_balance, create_bill, dictfetchone
)

@patient_required
def payment_history(request):
    """View payment history"""
    patient_id = request.session.get('user_id')
    
    # Get patient's bills
    bills = get_patient_bills(patient_id)
    
    # Get wallet balance
    patient = get_patient(patient_id)
    wallet_balance = patient['wallet_balance']
    
    return render(request, 'payments/payment_history.html', {
        'bills': bills,
        'wallet_balance': wallet_balance
    })

@patient_required
def pay_bill(request, bill_id):
    """Pay a bill view"""
    patient_id = request.session.get('user_id')
    
    # Check if bill exists and belongs to this patient
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM bill WHERE bill_id = %s AND patient_id = %s",
            [bill_id, patient_id]
        )
        bill = dictfetchone(cursor)
    
    if not bill:
        messages.error(request, "Bill not found or you don't have permission to view it.")
        return redirect('payment_history')
    
    # Get patient's wallet balance
    patient = get_patient(patient_id)
    wallet_balance = patient['wallet_balance']
    
    if request.method == 'POST':
        wallet_pin = request.POST.get('wallet_pin')
        
        if not wallet_pin:
            messages.error(request, "Please enter your wallet PIN.")
            return render(request, 'payments/pay_bill.html', {'bill': bill, 'wallet_balance': wallet_balance})
        
        # Process payment
        if pay_from_wallet(patient_id, bill['amount'], wallet_pin):
            # Update bill status
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM bill WHERE bill_id = %s",
                    [bill_id]
                )
            
            messages.success(request, "Payment successful.")
            return redirect('payment_history')
        else:
            messages.error(request, "Payment failed. Please check your wallet balance and PIN.")
    
    return render(request, 'payments/pay_bill.html', {
        'bill': bill,
        'wallet_balance': wallet_balance
    })

@patient_required
def topup_wallet(request):
    """Top up wallet view"""
    patient_id = request.session.get('user_id')
    
    # Get patient's wallet balance
    patient = get_patient(patient_id)
    wallet_balance = patient['wallet_balance']
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        wallet_pin = request.POST.get('wallet_pin')
        payment_method = request.POST.get('payment_method')
        
        if not all([amount, wallet_pin, payment_method]):
            messages.error(request, "Please fill in all fields.")
            return render(request, 'payments/topup_wallet.html', {'wallet_balance': wallet_balance})
        
        try:
            amount = Decimal(amount)
            if amount <= 0:
                messages.error(request, "Amount must be greater than zero.")
                return render(request, 'payments/topup_wallet.html', {'wallet_balance': wallet_balance})
        except ValueError:
            messages.error(request, "Invalid amount.")
            return render(request, 'payments/topup_wallet.html', {'wallet_balance': wallet_balance})
        
        # Process top-up
        if update_wallet_balance(patient_id, amount, wallet_pin):
            # Create bill record for the top-up
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO bill 
                    (patient_id, date, time, amount)
                    VALUES (%s, %s, %s, %s)
                    """,
                    [patient_id, datetime.now().date(), datetime.now().time(), amount]
                )
            
            messages.success(request, f"Successfully added {amount} to your wallet.")
            return redirect('payment_history')
        else:
            messages.error(request, "Top-up failed. Please check your wallet PIN.")
    
    return render(request, 'payments/topup_wallet.html', {
        'wallet_balance': wallet_balance
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
    
    return render(request, 'payments/invoice.html', {'bill': bill})

@patient_required
def invoice_topup(request, bill_id):
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
    
    return render(request, 'payments/invoice_topup.html', {'bill': bill})
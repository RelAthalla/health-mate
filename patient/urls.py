from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='patient_dashboard'),
    path('profile/', views.profile, name='patient_profile'),
    path('appointments/', views.appointments, name='patient_appointments'),
    path('appointments/request-otp/', views.request_otp, name='request_otp'),
    path('appointments/verify-firebase-token/', views.verify_firebase_token, name='verify_firebase_token'),
    path('find-doctors/', views.find_doctors, name='find_doctors'),
    path('prescriptions/', views.prescriptions, name='patient_prescriptions'),
    path('medical-history/', views.medical_history, name='medical_history'),
    path('wallet/', views.wallet, name='patient_wallet'),
    path('wallet/update-pin/', views.update_wallet_pin, name='update_wallet_pin'),
    path('wallet/topup/', views.topup_wallet, name='topup_wallet'),
    path('bills/', views.bills, name='patient_bills'),
    path('invoice/<int:bill_id>/', views.invoice, name='invoice'),

]
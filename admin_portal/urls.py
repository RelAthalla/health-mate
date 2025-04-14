from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='admin_dashboard'),
    path('patients/', views.manage_patients, name='manage_patients'),
    path('patients/<int:patient_id>/', views.patient_detail, name='admin_patient_detail'),
    path('doctors/', views.manage_doctors, name='manage_doctors'),
    path('doctors/<int:doctor_id>/', views.doctor_detail, name='admin_doctor_detail'),
    path('doctors/add/', views.add_doctor, name='add_doctor'),
    path('appointments/', views.appointments, name='admin_appointments'),
    path('prescriptions/', views.prescriptions, name='admin_prescriptions'),
    path('bills/', views.bills, name='admin_bills'),
    path('statistics/', views.statistics, name='admin_statistics'),
]
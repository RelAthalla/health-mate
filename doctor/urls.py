from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='doctor_dashboard'),
    path('profile/', views.profile, name='doctor_profile'),
    path('appointments/', views.appointments, name='doctor_appointments'),
    path('patients/', views.patients, name='doctor_patients'),
    path('patients/<int:patient_id>/', views.patient_detail, name='doctor_patient_detail'),
    path('patients/<int:patient_id>/prescriptions/create/', views.create_prescription_view, name='create_prescription'),
    path('schedule/', views.schedule, name='doctor_schedule'),
]
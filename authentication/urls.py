from django.urls import path
from . import views

urlpatterns = [
    path('patient/login/', views.patient_login, name='patient_login'),
    path('doctor/login/', views.doctor_login, name='doctor_login'),
    path('admin/login/', views.admin_login, name='admin_login'),
    path('logout/', views.logout_view, name='logout'),
]
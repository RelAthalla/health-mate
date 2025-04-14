from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.patient_register, name='patient_register'),
    path('logout/', views.logout_view, name='logout'),
]
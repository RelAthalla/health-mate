from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from .decorators import patient_required, doctor_required, admin_required
from .utils import get_all_doctors, get_doctors_by_specialization

def home(request):
    """Home page view"""

    if 'user_type' in request.session:
        user_type = request.session['user_type']
        if user_type == 'patient':
            return redirect('patient_dashboard')
        elif user_type == 'doctor':
            return redirect('doctor_dashboard')
        elif user_type == 'admin':
            return redirect('admin_dashboard')
        
    # Get featured doctors for home page
    featured_doctors = get_all_doctors()[:4]  # Limit to 4 doctors
    
    context = {
        'featured_doctors': featured_doctors,
        # 'user_type': user_type
    }
    
    return render(request, 'home.html', context)

def access_denied(request):
    """View for access denied page"""
    return render(request, 'access_denied.html')

def about(request):
    """About page view"""
    return render(request, 'about.html')

def contact(request):
    """Contact page view"""
    return render(request, 'contact.html')

@require_http_methods(["GET"])
def get_doctors_api(request):
    """API endpoint to get doctors by specialization"""
    specialization = request.GET.get('specialization', None)
    
    if specialization:
        doctors = get_doctors_by_specialization(specialization)
    else:
        doctors = get_all_doctors()
    
    return JsonResponse({
        'success': True,
        'doctors': doctors
    })

def error_404(request, exception):
    """Custom 404 error page"""
    return render(request, '404.html', status=404)

def error_500(request):
    """Custom 500 error page"""
    return render(request, '500.html', status=500)
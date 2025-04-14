from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('access-denied/', views.access_denied, name='access_denied'),
    path('api/doctors/', views.get_doctors_api, name='get_doctors_api'),
]

# Custom error handlers
handler404 = 'core.views.error_404'
handler500 = 'core.views.error_500'
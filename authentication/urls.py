from django.urls import path
from authentication.views import home, login, register, logout

app_name = 'authentication'

urlpatterns = [
    path('', home, name='home'),
    path('auth/login/', login, name='login'),
    path('auth/register/', register, name='register'),
    path('auth/logout/', logout, name='logout'),
]
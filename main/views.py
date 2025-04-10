from django.shortcuts import render

def home_view(request):
    role = "Guest"
    if request.user.is_authenticated:
        if request.user.is_staff:
            role = "Admin"
        else:
            role = "User"
    return render(request, 'home.html', {'role': role})

from django.shortcuts import render, redirect

class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of paths that don't require authentication
        exempt_paths = [
            '/patient/login/',
            '/doctor/login/',
            '/admin/login/',
            '/logout/',
            # Add other exempt paths here
        ]

        if not any(request.path.startswith(path) for path in exempt_paths):
            if 'user_type' not in request.session:
                return redirect('patient_login')  # or your preferred login page

        response = self.get_response(request)
        return response
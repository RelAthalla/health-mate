from django.db import connection

class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.ignored_paths = ['/static/', '/media/', '/favicon.ico']

    def __call__(self, request):
        response = self.get_response(request)
    
        if any(request.path.startswith(path) for path in self.ignored_paths):
            return response
        
        action = self._determine_action(request)
        
        if 'user_id' in request.session and 'user_type' in request.session and action:
            user_id = request.session.get('user_id')
            user_role = request.session.get('user_type')
            
            ip_address = request.META.get('REMOTE_ADDR', '')
            
            details = f"Path: {request.path}, Method: {request.method}"
            
            # input ke database
            self._log_to_database(user_id, user_role, action, ip_address, details)
            
        return response

    def _determine_action(self, request):
        """Tentukan jenis action berdasarkan path dan method.
        Hanya mengembalikan action jika termasuk dalam daftar yang diinginkan,
        yaitu login, logout, book_appointment, create_prescription, dan payment.
        Jika bukan salah satu dari action tersebut, return None.
        """
        path = request.path
        method = request.method
        
        if path.startswith('/auth/login'):
            return 'login'
        elif path.startswith('/auth/logout'):
            return 'logout'
        elif path.startswith('/appointments/book'):
            return 'book_appointment'
        elif path.startswith('/prescriptions/create'):
            return 'create_prescription'
        elif path.startswith('/payments'):
            return 'payment'
        
        # Jika bukan action di antara aciton di atas, return None, yang nantinya tidak akan di catat ke database
        return None

    def _log_to_database(self, user_id, user_role, action, ip_address, details):
        """Simpan log ke database"""
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO audit_log 
                    (user_id, user_role, action, ip_address, details)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    [user_id, user_role, action, ip_address, details]
                )
        except Exception as e:
            # Pesan sederhana jika terjadi gagal pencatatan ke database
            print(f"Error logging to audit_log: {str(e)}") 
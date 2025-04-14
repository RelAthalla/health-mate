from django.apps import AppConfig
import firebase_admin
from firebase_admin import credentials
from django.conf import settings

class PatientConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'patient'

    def ready(self):
        """Initialize Firebase when Django starts"""
        # Check if Firebase is already initialized
        if not firebase_admin._apps:
            try:
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred)
            except Exception as e:
                print(f"Firebase initialization error: {e}")
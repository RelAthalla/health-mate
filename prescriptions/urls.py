from django.urls import path
from . import views

urlpatterns = [
    path('view/<int:prescription_id>/', views.view_prescription, name='view_prescription'),
    path('create/', views.create_prescription_view, name='create_prescription_view'),
    path('download/<int:prescription_id>/', views.download_prescription, name='download_prescription'),
]
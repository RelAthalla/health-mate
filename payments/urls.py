from django.urls import path
from . import views

urlpatterns = [
    path('history/', views.payment_history, name='payment_history'),
    path('bill/<int:bill_id>/pay/', views.pay_bill, name='pay_bill'),
    path('wallet/topup/', views.topup_wallet, name='payments_topup_wallet'),
    path('invoice/<int:bill_id>/', views.invoice, name='invoice'),
    path('invoice-topup/<int:topup_id>/', views.invoice, name='invoice_topup'),
]
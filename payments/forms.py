from django import forms

class PaymentForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2, required=True,
                             min_value=10000, max_value=10000000,
                             widget=forms.NumberInput(attrs={
                                 'class': 'form-control',
                                 'placeholder': 'Enter amount',
                                 'min': '10000',
                                 'max': '10000000'
                             }))
    
    wallet_pin = forms.CharField(max_length=6, required=True, 
                              widget=forms.PasswordInput(attrs={
                                  'class': 'form-control',
                                  'placeholder': 'Enter wallet PIN',
                                  'pattern': '[0-9]{6}',
                                  'maxlength': '6'
                              }))
    
    payment_method = forms.ChoiceField(choices=[
        ('wallet', 'Wallet'),
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('e_wallet', 'E-Wallet')
    ], required=True, widget=forms.Select(attrs={
        'class': 'form-select'
    }))

class CreditCardForm(forms.Form):
    card_number = forms.CharField(max_length=19, required=True,
                               widget=forms.TextInput(attrs={
                                   'class': 'form-control',
                                   'placeholder': 'Card Number',
                                   'pattern': '[0-9]{13,19}',
                                   'maxlength': '19'
                               }))
    
    card_holder = forms.CharField(max_length=100, required=True,
                               widget=forms.TextInput(attrs={
                                   'class': 'form-control',
                                   'placeholder': 'Card Holder Name'
                               }))
    
    expiry_date = forms.CharField(max_length=5, required=True,
                               widget=forms.TextInput(attrs={
                                   'class': 'form-control',
                                   'placeholder': 'MM/YY',
                                   'pattern': '[0-9]{2}/[0-9]{2}',
                                   'maxlength': '5'
                               }))
    
    cvv = forms.CharField(max_length=4, required=True,
                       widget=forms.PasswordInput(attrs={
                           'class': 'form-control',
                           'placeholder': 'CVV',
                           'pattern': '[0-9]{3,4}',
                           'maxlength': '4'
                       }))
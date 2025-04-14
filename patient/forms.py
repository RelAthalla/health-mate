from django import forms

class PatientProfileForm(forms.Form):
    first_name = forms.CharField(max_length=50, required=True, 
                              widget=forms.TextInput(attrs={
                                 'class': 'form-control',
                                 'placeholder': 'First Name'
                              }))
    last_name = forms.CharField(max_length=50, required=True, 
                              widget=forms.TextInput(attrs={
                                 'class': 'form-control',
                                 'placeholder': 'Last Name'
                              }))
    phone = forms.CharField(max_length=20, required=True, 
                         widget=forms.TextInput(attrs={
                             'class': 'form-control',
                             'placeholder': 'Phone Number'
                         }))
    sex = forms.ChoiceField(choices=[
        ('Laki-laki', 'Laki-laki'),
        ('Perempuan', 'Perempuan')
    ], required=True, widget=forms.Select(attrs={
        'class': 'form-select'
    }))
    blood_type = forms.ChoiceField(choices=[
        ('A', 'A'),
        ('B', 'B'),
        ('AB', 'AB'),
        ('O', 'O')
    ], required=True, widget=forms.Select(attrs={
        'class': 'form-select'
    }))
    birthdate = forms.DateField(required=True, 
                             widget=forms.DateInput(attrs={
                                 'class': 'form-control',
                                 'type': 'date'
                             }))
    address = forms.CharField(required=True, 
                           widget=forms.Textarea(attrs={
                               'class': 'form-control',
                               'rows': 3,
                               'placeholder': 'Enter your address'
                           }))

class WalletPinForm(forms.Form):
    current_pin = forms.CharField(max_length=6, required=True, 
                               widget=forms.PasswordInput(attrs={
                                   'class': 'form-control',
                                   'placeholder': 'Current PIN',
                                   'pattern': '[0-9]{6}',
                                   'maxlength': '6'
                               }))
    new_pin = forms.CharField(max_length=6, required=True, 
                           widget=forms.PasswordInput(attrs={
                               'class': 'form-control',
                               'placeholder': 'New PIN',
                               'pattern': '[0-9]{6}',
                               'maxlength': '6'
                           }))
    confirm_pin = forms.CharField(max_length=6, required=True, 
                               widget=forms.PasswordInput(attrs={
                                   'class': 'form-control',
                                   'placeholder': 'Confirm New PIN',
                                   'pattern': '[0-9]{6}',
                                   'maxlength': '6'
                               }))
    
    def clean(self):
        cleaned_data = super().clean()
        new_pin = cleaned_data.get('new_pin')
        confirm_pin = cleaned_data.get('confirm_pin')
        
        if new_pin and confirm_pin and new_pin != confirm_pin:
            self.add_error('confirm_pin', "PINs don't match")
        
        # Validate PIN is 6 digits
        if new_pin and not (new_pin.isdigit() and len(new_pin) == 6):
            self.add_error('new_pin', "PIN must be 6 digits")
        
        return cleaned_data

class WalletTopUpForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2, required=True,
                             min_value=10000, max_value=10000000,
                             widget=forms.NumberInput(attrs={
                                 'class': 'form-control',
                                 'placeholder': 'Enter amount',
                                 'min': '10000',
                                 'max': '10000000'
                             }))
    pin = forms.CharField(max_length=6, required=True, 
                       widget=forms.PasswordInput(attrs={
                           'class': 'form-control',
                           'placeholder': 'Enter wallet PIN',
                           'pattern': '[0-9]{6}',
                           'maxlength': '6'
                       }))
    payment_method = forms.ChoiceField(choices=[
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('e_wallet', 'E-Wallet')
    ], required=True, widget=forms.Select(attrs={
        'class': 'form-select'
    }))
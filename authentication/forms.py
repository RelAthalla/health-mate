from django import forms

class LoginForm(forms.Form):
    phone = forms.CharField(max_length=20, required=True, 
                         widget=forms.TextInput(attrs={
                             'class': 'form-control',
                             'placeholder': 'Enter phone number'
                         }))
    password = forms.CharField(max_length=100, required=True, 
                             widget=forms.PasswordInput(attrs={
                                 'class': 'form-control',
                                 'placeholder': 'Enter password'
                             }))
    user_type = forms.ChoiceField(choices=[
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin')
    ], required=True, widget=forms.RadioSelect(attrs={
        'class': 'form-check-input'
    }))

class PatientRegistrationForm(forms.Form):
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
    password = forms.CharField(max_length=100, required=True, 
                             widget=forms.PasswordInput(attrs={
                                 'class': 'form-control',
                                 'placeholder': 'Create password'
                             }))
    confirm_password = forms.CharField(max_length=100, required=True, 
                                    widget=forms.PasswordInput(attrs={
                                        'class': 'form-control',
                                        'placeholder': 'Confirm password'
                                    }))
    wallet_pin = forms.CharField(max_length=6, required=True, 
                   widget=forms.PasswordInput(attrs={
                       'class': 'form-control',
                       'placeholder': 'Enter wallet pin (6 digits)'
                   }))
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords don't match")
        
        return cleaned_data
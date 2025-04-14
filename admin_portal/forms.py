from django import forms

class DoctorForm(forms.Form):
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
    specialization = forms.CharField(max_length=100, required=True,
                                  widget=forms.TextInput(attrs={
                                     'class': 'form-control',
                                     'placeholder': 'Specialization'
                                  }))
    experience = forms.IntegerField(required=True,
                                 widget=forms.NumberInput(attrs={
                                     'class': 'form-control',
                                     'placeholder': 'Years of Experience'
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
                               'placeholder': 'Address'
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
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords don't match")
        
        return cleaned_data
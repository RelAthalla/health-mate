from django import forms

class PrescriptionForm(forms.Form):
    patient_id = forms.IntegerField(widget=forms.HiddenInput())
    
    medicine = forms.CharField(required=True,
                            widget=forms.Textarea(attrs={
                                'class': 'form-control',
                                'rows': 4,
                                'placeholder': 'Enter medicine details'
                            }))
    
    advice = forms.CharField(required=True,
                          widget=forms.Textarea(attrs={
                              'class': 'form-control',
                              'rows': 4,
                              'placeholder': 'Enter advice for the patient'
                          }))
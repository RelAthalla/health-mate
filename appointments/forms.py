from django import forms
from datetime import datetime, timedelta

class AppointmentForm(forms.Form):
    date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': (datetime.now()).strftime('%Y-%m-%d'),
            'max': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        })
    )
    
    time = forms.TimeField(
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    def __init__(self, *args, **kwargs):
        available_times = kwargs.pop('available_times', None)
        super().__init__(*args, **kwargs)
        
        # Set time choices
        time_choices = []
        if available_times:
            time_choices = [(time.strftime('%H:%M'), time.strftime('%I:%M %p')) for time in available_times]
        else:
            # Default time slots (9 AM to 5 PM, every 30 minutes)
            start_time = datetime.strptime('09:00', '%H:%M')
            end_time = datetime.strptime('17:00', '%H:%M')
            current_time = start_time
            while current_time <= end_time:
                time_str = current_time.strftime('%H:%M')
                display_str = current_time.strftime('%I:%M %p')
                time_choices.append((time_str, display_str))
                current_time += timedelta(minutes=30)  # Tetap sebagai datetime
        self.fields['time'].widget.choices = time_choices
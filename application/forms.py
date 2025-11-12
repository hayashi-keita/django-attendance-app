from django import forms
from .models import Application

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['application_type', 'start_datetime', 'end_datetime', 'reason']
        widgets = {
            'application_type': forms.Select(attrs={'class': 'form-select'}),
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        labels = {
            'application_type': '申請種別',
            'srart_datetime': '開始日時',
            'end_datetime': '終了日時',
            'reason': '申請理由',
        }
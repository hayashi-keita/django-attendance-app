from django import forms
from .models import AttendanceRecord, BreakRecord
from django.contrib.auth import get_user_model

User = get_user_model()

class AttendanceRecordForm(forms.ModelForm):
    class Meta:
        model = AttendanceRecord
        fields = ['user', 'date', 'clock_in', 'clock_out', 'note']
        labels = {
            'user': '従業員',
            'date': '日付',
            'clock_in': '出勤',
            'clock_out': '退勤',
            'note': '備考',
        }
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'clock_in': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'clock_out': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        # 人事用にアクティブユーザーのみ選択可能
        self.fields['user'].queryset = User.objects.filter(is_active=True)

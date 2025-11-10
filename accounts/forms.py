from curses import use_env
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm, AuthenticationForm
from .models import CustomUser, Department, Team

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'manager']
        labels = {'name': '部署名', 'manager': '部長'}
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['department', 'name', 'manager']
        labels = {'department': '部署', 'name': '課名', 'manager': '課長'}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class HrCustomUserCreateForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'employee_number', 'department', 'team', 'full_name', 'gender')
        labels = {
            'username': 'ユーザー名',
            'email': 'メールアドレス',
            'role': '役割',
            'employee_number': '社員番号',
            'department': '所属部署',
            'team': '所属課',
            'full_name': '氏名',
            'gender': '性別',
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
    

class CustomUserCreateForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'employee_number', 'department', 'team', 'full_name', 'gender')
        labels = {
            'username': 'ユーザー名',
            'email': 'メールアドレス',
            'employee_number': '社員番号',
            'department': '所属部署',
            'team': '所属課',
            'full_name': '氏名',
            'gender': '性別',
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'employee'  # 社員固定
        user.is_active = False  # 仮登録
        if commit:
            user.save()
        return user

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'employee_number', 'department', 'team', 'full_name', 'gender')
        labels = {
            'username': 'ユーザー名',
            'email': 'メールアドレス',
            'role': '役割',
            'employee_number': '社員番号',
            'department': '所属部署',
            'team': '所属課',
            'full_name': '氏名',
            'gender': '性別',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if 'password' in self.fields:
            del self.fields['password']

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Department

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('追加情報', {'fields': ('role', 'employee_number', 'department', 'full_name', 'gender')}),
    )
    list_display = ('username', 'email', 'role', 'employee_number', 'department', 'full_name', 'gender')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Department)
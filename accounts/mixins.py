from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect

class EmployeeOnlyMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_employee
    
    def handle_no_permission(self):
        messages.error(self.request, 'このページにアクセスする権限がありません。')
        return redirect('attendance:index')

class ManagerOnlyMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_manager
    
    def handle_no_permission(self):
        messages.error(self.request, 'このページにアクセスする権限がありません。')
        return redirect('attendance:index')

class HrOnlyMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_hr
    
    def handle_no_permission(self):
        messages.error(self.request, 'このページにアクセスする権限がありません。')
        return redirect('attendance:index')

class EmployeeOrHrMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_employee or self.request.user.is_hr
    
    def handle_no_permission(self):
        messages.error(self.request, 'このページにアクセスする権限がありません。')
        return redirect('attendance:index')
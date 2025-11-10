from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordChangeDoneView
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .mixins import HrOnlyMixin
from .models import Department, Team, CustomUser
from .forms import (
    CustomAuthenticationForm, DepartmentForm, TeamForm, HrCustomUserCreateForm,
    CustomUserCreateForm, CustomUserChangeForm,
    PasswordChangeForm, AuthenticationForm)

# 部署関連
class DepartmentListView(HrOnlyMixin, ListView):
    model = Department
    template_name = 'accounts/department_list.html'

    def get_queryset(self):
        return Department.objects.order_by('pk')

class DepartmentCreateView(HrOnlyMixin, CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'accounts/hr_form.html'
    success_url = reverse_lazy('accounts:department_list')

class DepartmentUpdateView(HrOnlyMixin, UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'accounts/hr_form.html'
    success_url = reverse_lazy('accounts:department_list')

class DepartmentDeleteView(HrOnlyMixin, DeleteView):
    model = Department
    template_name = 'accounts/hr_delete.html'
    success_url = reverse_lazy('accounts:department_list')

# 課関連
class TeamListView(HrOnlyMixin, ListView):
    model = Team
    template_name = 'accounts/team_list.html'

    def get_queryset(self):
        return Team.objects.order_by('pk')

class TeamCreateView(HrOnlyMixin, CreateView):
    model = Team
    form_class = TeamForm
    template_name = 'accounts/hr_form.html'
    success_url = reverse_lazy('accounts:team_list')

class TeamUpdateView(HrOnlyMixin, UpdateView):
    model = Team
    form_class = TeamForm
    template_name = 'accounts/hr_form.html'
    success_url = reverse_lazy('accounts:team_list')

class TeamDeleteView(HrOnlyMixin, DeleteView):
    model = Team
    template_name = 'accounts/hr_delete.html'
    success_url = reverse_lazy('accounts:team_list')


# アカウント関連
#社員用アカウント作成画面
class SignUpView(CreateView):
    model = CustomUser
    form_class = CustomUserCreateForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:login')

# 人事用アカウント作成画面
class HrSignUpView(HrOnlyMixin, CreateView):
    model = CustomUser
    form_class = HrCustomUserCreateForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:profile_list')

class CustomUserLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'

class CustomUserListView(HrOnlyMixin, ListView):
    model = CustomUser
    template_name = 'accounts/profile_list.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = CustomUser.objects.select_related('department', 'team').order_by('pk')
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(username__icontains=q) | Q(full_name__icontains=q)
            )
        role = self.request.GET.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        department_pk_param = self.request.GET.get('department')
        if department_pk_param:
            try:
                department_pk = int(department_pk_param)
                queryset = queryset.filter(department=department_pk)
            except ValueError:
                pass
        approval = self.request.GET.get('approval')
        if approval == 'approved':
            queryset = queryset.filter(is_active=True)
        elif approval == 'unapproved':
            queryset = queryset.filter(is_active=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)      
        context['q'] = self.request.GET.get('q', '')
        context['role'] = self.request.GET.get('role', '')
        context['department'] = self.request.GET.get('department', '')
        context['approval'] = self.request.GET.get('approval', '')
        context['roles'] = CustomUser.ROLE_CHOICES
        context['departments'] = Department.objects.order_by('pk')
        context['unapproved_count'] = CustomUser.objects.filter(is_active=False).count()

        query_params = self.request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        context['current_filters_query'] = f'&{query_params.urlencode()}' if query_params else ''

        return context

"""人事専用：社員アカウントを承認するビュー"""
class UserApproveView(HrOnlyMixin, View):
    def post(self, request, *args, **kwargs):
        user = get_object_or_404(CustomUser, pk=kwargs['pk'])

        if not user.is_active:
            user.is_active = True
            user.save()
            messages.success(request, f'{user.full_name} さんを承認しました。')
        else:
            messages.info(request, f'{user.full_name} さんは既に承認済です。')
        
        return redirect('accounts:profile_list')

class CustomUserDetailView(HrOnlyMixin, DetailView):
    model = CustomUser
    template_name = 'accounts/profile_detail.html'

class CustomUserUpdateView(HrOnlyMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'accounts/profile_update.html'

    def get_success_url(self):
        return reverse('accounts:profile_detail', kwargs={'pk': self.object.pk})

class CustomUserDeleteView(HrOnlyMixin, DeleteView):
    model = CustomUser
    template_name = 'accounts/profile_delete.html'
    success_url = reverse_lazy('accounts:profile_list')

# パスワード変更関連
class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = PasswordChangeForm
    template_name ='accounts/password_change.html'
    success_url = reverse_lazy('accounts:password_change_done')

class CustomPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = 'accounts/password_change_done.html'
            
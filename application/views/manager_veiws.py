from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
from django.db.models import Q
from datetime import date, timedelta
from ..models import Application
from accounts.mixins import ManagerOnlyMixin

class MnagerApplicationListView(ManagerOnlyMixin, ListView):
    model = Application
    template_name = 'application/manager_application_list.html'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        manage_departments = user.manage_departments.all()
        manage_teams = user.manage_teams.all()
        # 自身が管理する部署に所属するユーザー
        q_department = Q(applicant__department__in=manage_departments)
        # 自身が管理する課に所属するユーザー
        q_team = Q(applicant__team__in=manage_teams)
        # クエリ取得
        queryset = Application.objects.filter(q_department | q_team).exclude(
            applicant=user,
        ).select_related(
            'applicant',
            'manager_approver',
            'hr_approver',
        ).order_by('status', '-created_at')
        
        # 追加フィルタリング
        status_param = self.request.GET.get('status')
        type_param = self.request.GET.get('application_type')
        start_date_param = self.request.GET.get('start_date')
        end_date_param = self.request.GET.get('end_date')
        applicant_name_param = self.request.GET.get('applicant_name')

        if status_param and status_param != 'all':
            queryset = queryset.filter(status=status_param)
        if type_param and type_param != 'all':
            queryset = queryset.filter(application_type=type_param)
        
        if start_date_param:
            try:
                start_date = date.fromisoformat(start_date_param)
                queryset = queryset.filter(start_datetime__gte=start_date)
            except ValueError:
                pass
        if end_date_param:
            try:
                end_date = date.fromisoformat(end_date_param)
                # 終了日に1日＋して、その日の00:00:00より前に申請を取得
                next_date = end_date + timedelta(days=1)
                queryset = queryset.filter(end_datetime__lt=next_date)
            except ValueError:
                pass
        
        if applicant_name_param:
            queryset = queryset.filter(applicant__full_name__icontains=applicant_name_param)

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # フィルタリング選択肢
        context['status_choices'] = Application.STATUS_CHOICES
        context['type_choices'] = Application.TYPE_CHOICES
        # 現在のフィルタ値
        context['current_status'] = self.request.GET.get('status', 'all')
        context['current_type'] = self.request.GET.get('application_type', 'all')
        context['start_date_filter_value'] = self.request.GET.get('start_date', '')
        context['end_date_filter_value'] = self.request.GET.get('end_date', '')
        context['applicant_name_filter_value'] = self.request.GET.get('applicant_name', '')

        query_params = self.request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        context['current_filters_query'] = f'&{query_params.urlencode()}' if query_params else ''
        
        return context

class ManagerApplicationDetailView(ManagerOnlyMixin, DetailView):
    model = Application
    template_name = 'application/manager_application_detail.html'

    def get_queryset(self):
        user = self.request.user
        manage_departments = user.manage_departments.all()
        manage_teams = user.manage_teams.all()

        q_department = Q(applicant__department__in=manage_departments)
        q_team = Q(applicant__team__in=manage_teams)

        queryset = Application.objects.filter(q_department | q_team).exclude(
            applicant=user,
        ).select_related(
            'applicant',
            'manager_approver',
            'hr_approver',
        ).order_by('status', '-created_at')

        return queryset
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = self.request.user

        if 'approve' in request.POST:
            if self.object.status == 'pending_manager':
                self.object.approve_by_manager(user)
                messages.success(request, '申請を承認しました。')
            else:
                messages.warning(request, '申請できない状態です。')
        
        elif 'reject' in request.POST:
            if self.object.status == 'pending_manager':
                reason = request.POST.get('rejection_reason', '').strip()
                if not reason:
                    messages.error(request, '却下の理由は必須です。')
                    return redirect('application:manager_application_detail', pk=self.object.pk)

                self.object.reject(user, reason=reason)
                messages.success(request, '申請を却下しました。')
            else:
                messages.warning(request, '却下できない状態です。')
        
        elif 'send_back' in request.POST:
            reason = request.POST.get('sed_back_reason', '').strip()
            if self.object.status == 'pending_manager':
                if not reason:
                    messages.error(request, '差し戻し理由は必須です。')
                    return redirect('application:manager_application_detail', pk=self.object.pk)
            
                self.object.send_back(user, reason=reason)
                messages.success(request, '申請を社員に差し戻しました。')
            else:
                messages.warning(request, '差し戻せない状態です。')
        
        return redirect('application:manager_application_detail', pk=self.object.pk)
            
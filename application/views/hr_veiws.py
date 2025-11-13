from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic import ListView, DetailView
from datetime import date, timedelta
from ..models import Application
from accounts.mixins import HrOnlyMixin
from notifications.utils import create_notification


class HrApplicationListView(HrOnlyMixin, ListView):
    model = Application
    template_name = 'application/hr_application_list.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = Application.objects.filter(
            status__in=['pending_hr', 'approved', 'rejected'],
        ).select_related(
            'applicant',
            'manager_approver',
            'hr_approver',
        ).order_by('-created_at')

        status_param = self.request.GET.get('status')
        type_param = self.request.GET.get('application_type')
        applicant_name_param = self.request.GET.get('applicant_name')
        start_date_param = self.request.GET.get('start_date')
        end_date_param = self.request.GET.get('end_date')

        if status_param and status_param != 'all':
            queryset = queryset.filter(status=status_param)

        if type_param and type_param != 'all':
            queryset = queryset.filter(application_type=type_param)
        
        if applicant_name_param:
            queryset = queryset.filter(applicant__full_name__icontains=applicant_name_param)
        
        if start_date_param:
            try:
                start_date = date.fromisoformat(start_date_param)
                queryset = queryset.filter(start_datetime__gte=start_date)
            except ValueError:
                pass
        if end_date_param:
            try:
                end_date = date.fromisoformat(end_date_param)
                next_date = end_date + timedelta(days=1)
                queryset = queryset.filter(end_datetime__lt=next_date)
            except ValueError:
                pass
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Application.STATUS_CHOICES
        context['type_choices'] = Application.TYPE_CHOICES

        context['current_status'] = self.request.GET.get('status', 'all')
        context['current_type'] = self.request.GET.get('application_type', 'all')
        context['applicant_name_filter_value'] = self.request.GET.get('applicant_name', '')
        context['start_date_filter_value'] = self.request.GET.get('start_date', '')
        context['end_date_filter_value'] = self.request.GET.get('end_date', '')

        query_params = self.request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        context['current_filters_query'] = f'&{query_params.urlencode()}' if query_params else ''

        return context
    
class HrApplicationDetailView(HrOnlyMixin, DetailView):
    model = Application
    template_name = 'application/hr_application_detail.html'

    def get_queryset(self):
        return Application.objects.filter(
            status__in=['pending_manager','pending_hr', 'approved',]
        ).select_related(
            'applicant',
            'manager_approver',
            'hr_approver',
        )
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = request.user

        if 'approve' in request.POST:
            if self.object.status == 'pending_hr':
                self.object.approve_by_hr(user)
                messages.success(request, '申請を承認しました。')
                # 通知
                create_notification(
                    sender=user,
                    recipient=self.object.applicant,
                    message=f'あなたの申請『{self.object.get_application_type_display()}』が人事に承認されました。',
                    link_name='application:application_detail',
                    pk=self.object.pk
                )
            else:
                messages.warning(request, '承認できない状態です。')

        elif 'send_back' in request.POST:
            if self.object.status in ['pending_hr', 'approved' ]:
                reason = request.POST.get('send_back_reason', '').strip()
                if not reason:
                    messages.error(request, '差し戻し理由は必須です。')
                    return redirect('application:hr_application_detail', pk=self.object.pk)
                
                cancel = True if self.object.status == 'approved' else False
                self.object.send_back(user, reason=reason, cancel_approval=cancel)
                messages.success(request, '申請を人事承認待ちに差し戻しました。')
                # 通知
                create_notification(
                    sender=user,
                    recipient=self.object.applicant,
                    message=f'あなたの申請『{self.object.get_application_type_display()}』が人事に差し戻しされました。',
                    link_name='application:application_detail',
                    pk=self.object.pk
                )
            else:
                messages.warning(request, '差し戻せない状態です。')
        
        return redirect('application:hr_application_detail', pk=self.object.pk)
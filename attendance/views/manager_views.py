from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth import get_user_model
from django.contrib import messages
from accounts.mixins import ManagerOnlyMixin
from django.db.models import Prefetch
from ..models import AttendanceRecord
from ..forms import AttendanceRecordForm
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from datetime import date, timedelta
from django.utils import timezone

CustomUser = get_user_model()

class ManagerAttendanceListView(ManagerOnlyMixin, ListView):
    model = CustomUser
    template_name = 'attendance/manager_attendance_list.html'
    paginate_by = 10

    def get_default_date(self):
        return date.today()

    def get_queryset(self):
        manage_departments = self.request.user.manage_departments.all()
        date_param = self.request.GET.get('date')

        if date_param:
            try:
                selected_date = date.fromisoformat(date_param)
            except ValueError:
                selected_date = self.get_default_date()
        else:
            selected_date = self.get_default_date()

        self.selected_date = selected_date

        # 対象ユーザー
        queryset = CustomUser.objects.filter(
            department__in=manage_departments,
            role='employee',
        ).order_by('employee_number')

        # 対象ユーザーに限定した出勤データ
        record_for_date = AttendanceRecord.objects.filter(
            date=self.selected_date,
        ).select_related('read_by')

        # Prefetch
        queryset = queryset.prefetch_related(
            Prefetch('attendance_records', queryset=record_for_date, to_attr='record_of_the_day')
        )

        # フィルタ
        status_param = self.request.GET.get('status')
        if status_param == 'submitted':
            queryset = queryset.filter(attendance_records__date=self.selected_date).distinct()
        elif status_param == 'unsubmitted':
            queryset = queryset.exclude(attendance_records__date=self.selected_date).distinct()

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_date'] = self.selected_date
        context['date_filter_value'] = self.selected_date.isoformat()
        context['selected_status'] = self.request.GET.get('status', 'all')
        
        unread_record_count = AttendanceRecord.objects.filter(
            user__department__in=self.request.user.manage_departments.all(),
            date=self.selected_date,
            is_read=False,
        ).count()
        context['unread_record_count'] = unread_record_count

        query_params = self.request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        context['current_filters_query'] = f'&{query_params.urlencode()}' if query_params else ''

        return context
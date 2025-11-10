from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from accounts.mixins import HrOnlyMixin
from ..models import AttendanceRecord
from ..forms import AttendanceRecordForm
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from datetime import date, timedelta
from django.utils import timezone

class HrAttendanceListView(HrOnlyMixin, ListView):
    model = AttendanceRecord
    template_name = 'attendance/hr_attendance_list.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = AttendanceRecord.objects.select_related('user')
        
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(user__username__icontains=q) | Q(user__full_name__icontains=q)
            )
        
        start_date_param = self.request.GET.get('start_date')
        end_date_param = self.request.GET.get('end_date')
        if start_date_param:
            try:
                start_date_obj = date.fromisoformat(start_date_param)
                queryset = queryset.filter(date__gte=start_date_obj)
            except ValueError:
                pass
        if end_date_param:
            try:
                end_date_obj = date.fromisoformat(end_date_param)
                queryset = queryset.filter(date__lte=end_date_obj)
            except ValueError:
                pass
        
        selected_read_status = self.request.GET.get('read_status', 'all')
        if selected_read_status == 'unread':
            queryset = queryset.filter(is_read=False)
        
        elif selected_read_status == 'read':
            queryset = queryset.filter(is_read=True)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['q'] = self.request.GET.get('q', '')
        context['start_date_filter_value'] = self.request.GET.get('start_date', '')
        context['end_date_filter_value'] = self.request.GET.get('end_date', '')
        context['selected_read_status'] = self.request.GET.get('read_status', 'all')
        context['unread_record_count'] = self.get_queryset().filter(is_read=False).count()

        query_params = self.request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        context['current_filters_query'] = f'&{query_params.urlencode()}' if query_params else ''
        
        return context

class HrAttendanceCreateView(HrOnlyMixin, CreateView):
    model = AttendanceRecord
    form_class = AttendanceRecordForm
    template_name = 'attendance/hr_attendance_form.html'
    success_url = reverse_lazy('attendance:attendance_list')

    def get_default_date(self):
        today = date.today()
        weekday = today.weekday()

        if weekday == 0:
            default_date = today - timedelta(days=3)
        elif weekday == 6:
            default_date = today - timedelta(days=2)
        else: 
            default_date = today - timedelta(days=1)
        return default_date
    
    def get_initial(self):
        return {'date': self.get_default_date()}
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['default_record_date'] = self.get_default_date()
        return context
    
    def form_valid(self, form):
        user = form.cleaned_data.get('user')
        record_date = form.cleaned_data.get('date')

        if AttendanceRecord.objects.filter(user=user, date=record_date).exists():
            messages.error(self.request, f'{user} さんの {record_date} の勤怠は既に登録されています。')
            return redirect(self.success_url)
        
        messages.success(self.request, f'{user} さんの {record_date} の勤怠を登録しました。')
        
        return super().form_valid(form)

class HrAttendanceDetailView(HrOnlyMixin, DetailView):
    model = AttendanceRecord
    template_name = 'attendance/attendance_detail.html'

    def get_queryset(self):
        return AttendanceRecord.objects.select_related('user', 'read_by').prefetch_related('breaks')
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if 'mark_read' in request.POST:
            self.object.is_read = True
            self.object.read_by = request.user
            self.object.read_at = timezone.now()
            self.object.save()
        elif 'unmark_read' in request.POST:
            self.object.is_read = False
            self.object.read_by = None
            self.object.read_at = None
            self.object.save()
        
        return redirect('attendance:hr_attendance_detail', pk=self.object.pk)

class HrAttendanceUpdateView(HrOnlyMixin, UpdateView):
    model = AttendanceRecord
    form_class = AttendanceRecordForm
    template_name = 'attendance/hr_attendance_form.html'
    
    def get_queryset(self):
        return AttendanceRecord.objects.select_related('user')
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.is_read:
            messages.error(self.request, '確認済のデータは編集できません。')
            return redirect('attendance:hr_attendance_list')
        return obj
    
    def form_valid(self, form):
        user = form.cleaned_data.get('user')
        record_date = form.cleaned_data.get('date')
        messages.success(self.request, f'{user} さんの {record_date} の勤怠データを更新しました。')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('attendance:hr_attendance_detail', kwargs={'pk':self.object.pk})

class HrAttendanceDeleteView(HrOnlyMixin, DeleteView):
    model = AttendanceRecord
    template_name = 'attendance/hr_attendance_delete.html'
    success_url = reverse_lazy('attendance:hr_attendance_list')

    def get_queryset(self):
        return AttendanceRecord.objects.select_related('user')
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.is_read:
            messages.warning(self.request, '確認済のデータは削除できません。')
            return redirect('attendance:hr_attendance_list')
        return obj

    def delete(self, request, *args, **kwargs):
        record = self.get_object()
        messages.success(self.request, f'{record.user} さんの {record.date} 分の勤怠データを削除しました。')
        return super().delete(request, *args, **kwargs)
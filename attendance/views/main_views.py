from django.views.generic import TemplateView, CreateView, ListView, DetailView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.shortcuts import redirect, render
from datetime import date
from ..models import AttendanceRecord, BreakRecord
from ..forms import AttendanceRecordForm

class Index(TemplateView):
    template_name = 'attendance/index.html'

class AttendanceDashboardView(LoginRequiredMixin, View):
    template_name = 'attendance/attendance_dashboard.html'

    def get(self, request):
        """出勤・退勤・休憩打刻をすべて扱う単一ビュー"""
        today = timezone.localdate()
        record, _ = AttendanceRecord.objects.get_or_create(user=request.user, date=today)
        # 現在進行中の休憩（未終了のBreakRecord）
        active_break = record.breaks.filter(end_time__isnull=True).first()
        context = {'record': record, 'active_break':active_break}
       
        return render(request, self.template_name, context)
    
    def post(self, request):
        """出勤または退勤ボタン押下時の処理"""
        today = timezone.localdate()
        record, _ = AttendanceRecord.objects.get_or_create(user=request.user, date=today)
        action = request.POST.get('action')
        active_break = record.breaks.filter(end_time__isnull=True).first()
        now = timezone.localtime(timezone.now())
        note = request.POST.get('note', '')

        if action == 'clock_in':
            if record.clock_in:
                messages.warning(request, '既に出勤済みです。')
            else:
                record.clock_in = now
                record.save()
                messages.success(request, f"出勤時刻を登録しました：{now.strftime('%H:%M')}")
        
        elif action == 'clock_out':
            if not record.clock_in:
                messages.warning(request, '出勤していません。先に出勤を記録してください。')
            elif record.clock_out:
                messages.warning(request, '既に退勤済みです。')
            else:
                record.clock_out = now
                record.calculate_total_work_time()
                record.save()
                messages.success(request, f"退勤時刻を登録しました：{now.strftime('%H:%M')}")
        
        elif action == 'break_start':
            if active_break:
                messages.warning(request, '既に休憩中です。')
            else:
                BreakRecord.objects.create(attendance=record, start_time=now)
                messages.success(request, f"休憩を開始しました：{now.strftime('%H:%M')}")
        
        elif action == 'break_end':
            if not active_break:
                messages.warning(request, '開始中の休憩はありません。')
            else:
                active_break.end_time = now
                active_break.save()
                record.calculate_total_work_time()
                messages.success(request, f"休憩を終了しました：{now.strftime('%H:%M')}")
        
        elif action == 'update_note':
            record.note = note
            record.save()
            messages.success(request, '備考を更新しました。')
        
        return redirect('attendance:dashboard')

class AttendanceListView(LoginRequiredMixin, ListView):
    model = AttendanceRecord
    template_name = 'attendance/attendance_list.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = AttendanceRecord.objects.filter(user=self.request.user)

        self.start_date_param = self.request.GET.get('start_date')
        self.end_date_param = self.request.GET.get('end_date')
        self.selected_read_status = self.request.GET.get('read_status', 'all')
        # start_date 処理: 開始日以降
        if self.start_date_param:
            try:
                start_date_obj = date.fromisoformat(self.start_date_param)
                queryset = queryset.filter(date__gte=start_date_obj)
            except ValueError:
                pass
        # end_date 処理: 終了日以前
        if self.end_date_param:
            try:
                end_date_obj = date.fromisoformat(self.end_date_param)
                queryset = queryset.filter(date__lte=end_date_obj)
            except ValueError:
                pass
        
        if self.selected_read_status == 'unread':
            queryset = queryset.filter(is_read=False)
        elif self.selected_read_status == 'read':
            queryset = queryset.filter(is_read=True)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['start_date_filter_value'] = self.start_date_param if self.start_date_param else ''
        context['end_date_filter_value'] = self.end_date_param if self.end_date_param else ''
        context['selected_read_status'] = self.selected_read_status
        context['unread_record_count'] = self.get_queryset().filter(user=self.request.user, is_read=False).count()

        query_params = self.request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        context['current_filters_query'] = f'&{query_params.urlencode()}' if query_params else ''
        
        return context

class AttendanceDetailView(LoginRequiredMixin, DetailView):
    model = AttendanceRecord
    template_name = 'attendance/attendance_detail.html'

    def get_queryset(self):
        return AttendanceRecord.objects.select_related('user')
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class AttendanceRecord(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        verbose_name='社員',
    )
    date = models.DateField(default=timezone.localdate, verbose_name='日付')
    clock_in = models.DateTimeField(blank=True, null=True, verbose_name='出勤時刻')
    clock_out = models.DateTimeField(blank=True, null=True, verbose_name='退勤時刻')
    total_work_time = models.DurationField(blank=True, null=True, verbose_name='実働時間')
    note = models.TextField(blank=True, verbose_name='備考')
    is_read = models.BooleanField(default=False, verbose_name='既読')
    read_at = models.DateTimeField(blank=True, null=True)
    read_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='checked_records',
        verbose_name='確認者',
    )

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']
        verbose_name = '勤怠記録'
        verbose_name_plural = '勤怠記録'
    
    def __str__(self):
        return f'{self.user.full_name} - {self.date}'
    
    def calculate_total_work_time(self):
        if self.clock_in and self.clock_out:
            total = self.clock_out - self.clock_in
            total_break = sum((b.duration for b in self.breaks.all()), timedelta())
            self.total_work_time = total - total_break
            self.save()
    @property
    def formatted_work_time(self):
        if not self.total_work_time:
            return "-"
        total_seconds = int(self.total_work_time.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f'{hours}時間{minutes}分' if hours > 0 else f'{minutes}分'

class BreakRecord(models.Model):
    attendance = models.ForeignKey(
        AttendanceRecord,
        on_delete=models.CASCADE,
        related_name='breaks',
        verbose_name='勤怠記録',
    )
    start_time = models.DateTimeField(verbose_name='休憩開始')
    end_time = models.DateTimeField(blank=True, null=True, verbose_name='休憩終了')

    class Meta:
        verbose_name = '休憩記録'
        verbose_name_plural = '休憩記録'
    
    def __str__(self):
        return f"{self.attendance.user.full_name} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def duration(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return timedelta()
    
    @property
    def formatted_duration(self):
        if not self.start_time or not self.end_time:
            return '計算中'
        total_seconds = int(self.duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f'{hours}時間{minutes}分' if hours > 0 else f'{minutes}分'
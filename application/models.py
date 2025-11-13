from django.db import models
from django.conf import settings
from django.utils import timezone

class Application(models.Model):
    TYPE_CHOICES = [
        ('paid_leave', '有給休暇'),
        ('late', '遅刻'),
        ('early_leave', '早退'),
        ('absence', '欠勤'),
        ('business_trip', '出張'),
        ('remote', '在宅勤務'),
        ('ather', 'その他'),
    ]
    STATUS_CHOICES = [
        ('pending_manager', '上司承認待ち'),
        ('pending_hr', '人事承認待ち'),
        ('approved', '承認済'),
        ('rejected', '却下'),
    ]

    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name='申請者',
    )
    manager_approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='manager_approved_applications',
        verbose_name='上司承認者',
    )
    hr_approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='hr_approved_applications',
        verbose_name='人事承認者',
    )
    manager_approved_at = models.DateTimeField(blank=True, null=True, verbose_name='上司承認日時')
    hr_approved_at = models.DateTimeField(blank=True, null=True, verbose_name='人事承認日時')
    application_type = models.CharField(max_length=50, choices=TYPE_CHOICES, verbose_name='申請種別')
    reason = models.TextField(verbose_name='申請理由')
    start_datetime = models.DateTimeField(verbose_name='開始日時')
    end_datetime = models.DateTimeField(blank=True, null=True, verbose_name='終了日時')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending_manager', verbose_name='ステータス')
    rejection_reason = models.TextField(blank=True, null=True, verbose_name='却下理由')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='申請日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        verbose_name = '各種申請'
        verbose_name_plural = '各種申請'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.get_application_type_display()} - {self.applicant.full_name }（{self.get_status_display()}）'
    
    # 状態変更メソッド
    def approve_by_manager(self, user):
        self.manager_approver = user
        self.manager_approved_at = timezone.now()
        self.status = 'pending_hr'
        self.rejection_reason = None
        self.save()

    def approve_by_hr(self, user):
        self.hr_approver = user
        self.hr_approved_at = timezone.now()
        self.status = 'approved'
        self.rejection_reason = None
        self.save()
    
    def reject(self, user, reason=None):
        if user.is_manager:
            self.manager_approver = user
        elif user.is_hr:
            self.hr_approver = user
        self.status = 'rejected'
        self.rejection_reason = reason
        self.save()
    
    def send_back(self, user, reason=None, cancel_approval=False):
        if self.status not in ['pending_manager', 'pending_hr', 'approved']:
            raise ValueError('この申請は差し戻しできません。')
        
        if user.is_manager:
            self.status = 'pending_manager'
            self.manager_approver = None
        elif user.is_hr:
            if cancel_approval:
                self.status = 'pending_hr'
                self.hr_approver = None
            else:
                self.status = 'pending_manager'
                self.hr_approver = None
        
        self.rejection_reason = reason
        self.save()


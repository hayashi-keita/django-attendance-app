from django.db import models
from django.conf import settings

class Notification(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        verbose_name='送信者',
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_notifications',
        verbose_name='受信者',
    )
    link = models.URLField(blank=True, null=True, verbose_name='詳細画面')
    message = models.CharField(max_length=255, verbose_name='メッセージ')
    is_read = models.BooleanField(default=False, verbose_name='既読')
    created_at =models.DateTimeField(auto_now_add=True, verbose_name='作成日')

    def __str__(self):
        return f'{self.recipient} - {self.message[:20]}'

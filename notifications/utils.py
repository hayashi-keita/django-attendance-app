from django.urls import reverse
from .models import Notification

def create_notification(sender, recipient, message, link_name, pk):
    Notification.objects.create(
        sender=sender,
        recipient=recipient,
        message=message,
        link=reverse(link_name, kwargs={'pk': pk})
    )
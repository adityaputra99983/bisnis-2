from django.contrib.auth.models import User
from .models import Notification


def create_notification(user, title, message, notification_type='system', link=''):
    if user and user.is_authenticated:
        return Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link,
        )
    return None


def get_unread_count(user):
    if user and user.is_authenticated:
        return Notification.objects.filter(user=user, is_read=False).count()
    return 0


def get_recent_notifications(user, limit=10):
    if user and user.is_authenticated:
        return Notification.objects.filter(user=user)[:limit]
    return Notification.objects.none()

from healers.models import Notification


def notification_context(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {'global_unread_notifications': unread_count}
    return {'global_unread_notifications': 0}

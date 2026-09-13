from .models import Notification


def create_notification(*, user, type, title, message='', link='', metadata=None):
    return Notification.objects.create(
        user=user,
        type=type,
        title=title,
        message=message,
        link=link or '',
        metadata=metadata or {},
    )

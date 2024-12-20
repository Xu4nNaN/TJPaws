from .models import Notification


def create_notification(receiver, notification_type, content, related_id=None):
    """
    创建一条通知并保存到数据库。

    :param receiver: 通知接收者 (User instance)
    :param notification_type: 通知类型 (str, 参见 Notification.NOTIFICATION_TYPES)
    :param content: 通知内容 (str)
    :param related_id: 相关对象的 id (int)
    """
    Notification.objects.create(
        receiver=receiver,# TODO 这里我给改成了receiver，原来是user，和model对不上；有错的话改回来
        notification_type=notification_type,
        content=content,
        related_id=related_id
    )
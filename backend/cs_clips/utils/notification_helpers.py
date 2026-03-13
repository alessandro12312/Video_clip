def create_notification(
    recipient, sender=None, type=None, video=None, comment=None, contest=None
):
    """Crea una notifica, skippando se sender == recipient (no self-notification)."""
    if sender and sender == recipient:
        return None
    from cs_clips.models import Notification

    return Notification.objects.create(
        recipient=recipient,
        sender=sender,
        type=type,
        video=video,
        comment=comment,
        contest=contest,
    )

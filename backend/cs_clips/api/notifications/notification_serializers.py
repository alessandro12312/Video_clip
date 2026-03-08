from rest_framework import serializers

from cs_clips.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    sender_username = serializers.ReadOnlyField(source="sender.username")
    video_title = serializers.ReadOnlyField(source="video.title")
    type_display = serializers.CharField(source="get_type_display", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "recipient",
            "sender",
            "sender_username",
            "type",
            "type_display",
            "is_read",
            "created_at",
            "video",
            "video_title",
            "comment",
            "contest",
        ]
        read_only_fields = [
            "id",
            "recipient",
            "sender",
            "sender_username",
            "type",
            "type_display",
            "is_read",
            "created_at",
            "video",
            "video_title",
            "comment",
            "contest",
        ]

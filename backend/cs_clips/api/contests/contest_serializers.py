# Contest serializer
from rest_framework import serializers

from cs_clips.api.videos.video_serializers import VideoOutputSerializer
from cs_clips.models import Contest


class ContestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contest
        fields = (
            "id",
            "name",
            "tag",
            "start_date",
            "end_date",
            "is_closed",
            "closed_at",
        )
        extra_kwargs = {"tag": {"required": True}}


class ContestListOutputSerializer(serializers.ModelSerializer):
    video_count = serializers.IntegerField(read_only=True)
    winner_title = serializers.CharField(
        source="winner.title", read_only=True, default=None
    )

    class Meta:
        model = Contest
        fields = [
            "id",
            "name",
            "tag",
            "start_date",
            "end_date",
            "is_closed",
            "closed_at",
            "winner",
            "winner_title",
            "video_count",
        ]
        read_only_fields = fields


class ContestDetailOutputSerializer(ContestListOutputSerializer):
    winner_detail = VideoOutputSerializer(source="winner", read_only=True)

    class Meta(ContestListOutputSerializer.Meta):
        fields = ContestListOutputSerializer.Meta.fields + ["winner_detail"]
        read_only_fields = fields

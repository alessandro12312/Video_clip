# Contest serializer
from rest_framework import serializers

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

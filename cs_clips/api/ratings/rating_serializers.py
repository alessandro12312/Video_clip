# Rating serializer
from rest_framework import serializers
from cs_clips.models import Rating


class RatingSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Rating
        fields = ('id', 'user', 'video', 'value', 'created_at', 'updated_at')
        read_only_fields = ('timestamp', 'created_at', 'updated_at')
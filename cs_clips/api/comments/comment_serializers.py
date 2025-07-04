# Comment serializer
from rest_framework import serializers
from cs_clips.models import Comment


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Comment
        fields = ('id', 'user', 'video', 'content', 'timestamp_second', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
    
    def validate(self, data):
        """
        Valida che timestamp_second sia >= 0 e non superi la durata del video.
        """
        timestamp = data.get('timestamp_second')
        if timestamp is None:
            timestamp = 0
        video = data.get('video')
        if timestamp < 0:
            raise serializers.ValidationError({
                "timestamp_second": "Il valore deve essere maggiore o uguale a 0."
            })
        if not video or video.duration is None:
            raise serializers.ValidationError({
                "video": "Il video deve avere una durata impostata."
            })
        if timestamp > video.duration:
            raise serializers.ValidationError({
                "timestamp_second": f"Il valore non può superare la durata del video ({video.duration} secondi)."
            })
        return data
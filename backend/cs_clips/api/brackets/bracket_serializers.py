from django.db.models import Avg, F, Q
from rest_framework import serializers

from cs_clips.models import Bracket, ContestEntry, Matchup


class ContestEntryNestedSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    video_id = serializers.IntegerField(source="video.id", read_only=True)
    video_title = serializers.CharField(source="video.title", read_only=True)
    video_thumbnail_url = serializers.CharField(
        source="video.thumbnail_url", read_only=True, default=None
    )

    class Meta:
        model = ContestEntry
        fields = [
            "id",
            "user_id",
            "username",
            "video_id",
            "video_title",
            "video_thumbnail_url",
        ]
        read_only_fields = fields


class MatchupOutputSerializer(serializers.ModelSerializer):
    entry_1 = ContestEntryNestedSerializer(read_only=True)
    entry_2 = ContestEntryNestedSerializer(read_only=True)
    winner = serializers.PrimaryKeyRelatedField(read_only=True)
    avg_rating_1 = serializers.FloatField(read_only=True, default=None)
    avg_rating_2 = serializers.FloatField(read_only=True, default=None)

    class Meta:
        model = Matchup
        fields = [
            "id",
            "round_number",
            "position",
            "entry_1",
            "entry_2",
            "winner",
            "is_completed",
            "avg_rating_1",
            "avg_rating_2",
        ]
        read_only_fields = fields


class BracketListOutputSerializer(serializers.ModelSerializer):
    entries_count = serializers.IntegerField(read_only=True)
    created_by_username = serializers.CharField(
        source="created_by.username", read_only=True
    )

    class Meta:
        model = Bracket
        fields = [
            "id",
            "name",
            "description",
            "status",
            "max_participants",
            "current_round",
            "entries_count",
            "created_by",
            "created_by_username",
            "created_at",
            "prize_description",
        ]
        read_only_fields = fields


class BracketDetailOutputSerializer(BracketListOutputSerializer):
    matchups_by_round = serializers.SerializerMethodField()
    my_entry = serializers.SerializerMethodField()

    class Meta(BracketListOutputSerializer.Meta):
        fields = BracketListOutputSerializer.Meta.fields + [
            "matchups_by_round",
            "my_entry",
        ]
        read_only_fields = fields

    def get_matchups_by_round(self, obj):
        matchups = (
            obj.matchups.select_related(
                "entry_1__user",
                "entry_1__video",
                "entry_2__user",
                "entry_2__video",
                "winner",
            )
            .annotate(
                avg_rating_1=Avg("votes__value", filter=Q(votes__entry=F("entry_1"))),
                avg_rating_2=Avg("votes__value", filter=Q(votes__entry=F("entry_2"))),
            )
            .order_by("round_number", "position")
        )

        rounds = {}
        for matchup in matchups:
            rn = matchup.round_number
            if rn not in rounds:
                rounds[rn] = []
            rounds[rn].append(
                MatchupOutputSerializer(matchup, context=self.context).data
            )
        return rounds

    def get_my_entry(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        entry = obj.entries.filter(user=request.user).first()
        if entry:
            return ContestEntryNestedSerializer(entry).data
        return None


class EnterBracketInputSerializer(serializers.Serializer):
    video_id = serializers.IntegerField()


class VoteMatchupInputSerializer(serializers.Serializer):
    entry = serializers.PrimaryKeyRelatedField(queryset=ContestEntry.objects.all())
    value = serializers.IntegerField(min_value=1, max_value=5)

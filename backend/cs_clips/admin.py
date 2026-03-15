from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone

from cs_clips.models import (
    Bracket,
    Comment,
    CommentLike,
    Contest,
    ContestEntry,
    Matchup,
    MatchupVote,
    Notification,
    Rating,
    User,
    Video,
    VideoLike,
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User

    # Colonne nella lista utenti
    list_display = (
        "username",
        "email",
        "is_staff",
        "is_superuser",
        "role",
        "followers_count",
        "following_count",
    )
    list_filter = ("is_staff", "is_superuser", "groups")
    search_fields = ("username", "email")
    ordering = ("username",)

    # Rende readonly le liste follower/following
    readonly_fields = ["followers_list", "following_list", "last_login", "date_joined"]

    # Campi organizzati in sezioni
    fieldsets = (
        ("Informazioni account", {"fields": ("username", "email", "password")}),
        (
            "Permessi",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Date e accessi", {"fields": ("last_login", "date_joined")}),
        ("Relazioni social", {"fields": ("followers_list", "following_list")}),
    )

    # Gruppi visibili al momento della creazione
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                    "groups",
                ),
            },
        ),
    )

    def role(self, obj):
        if obj.is_superuser:
            return "admin"
        groups = obj.groups.all()
        return groups[0].name if groups else "-"

    role.short_description = "Ruolo"

    def followers_list(self, obj):
        return ", ".join([u.username for u in obj.followers.all()])

    followers_list.short_description = "Followers"

    def following_list(self, obj):
        return ", ".join([u.username for u in obj.following.all()])

    following_list.short_description = "Following"

    def followers_count(self, obj):
        return obj.followers.count()

    followers_count.short_description = "N° Followers"

    def following_count(self, obj):
        return obj.following.count()

    following_count.short_description = "N° Following"


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "uploader",
        "tag",
        "views",
        "allow_download",
        "created_at",
        "contest",
    )
    list_filter = ("tag", "uploader", "created_at")
    search_fields = ("title", "uploader__username")
    autocomplete_fields = ["uploader", "contest"]
    readonly_fields = ("created_at", "updated_at", "duration")


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("user", "video", "value", "created_at")
    list_filter = ("value",)
    search_fields = ("user__username", "video__title")
    autocomplete_fields = ["user", "video"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "video",
        "content_preview",
        "timestamp_second",
        "is_disabled",
        "created_at",
    )
    list_filter = ("is_disabled",)
    search_fields = ("user__username", "video__title", "content")
    autocomplete_fields = ["user", "video"]
    actions = ["disabilita_commenti", "abilita_commenti"]

    @admin.display(description="Anteprima contenuto")
    def content_preview(self, obj):
        """Mostra i primi 50 caratteri del commento."""
        if len(obj.content) > 50:
            return obj.content[:50] + "..."
        return obj.content

    @admin.action(description="Disabilita commenti selezionati")
    def disabilita_commenti(self, request, queryset):
        updated = queryset.update(is_disabled=True)
        self.message_user(request, f"{updated} commenti disabilitati.")

    @admin.action(description="Abilita commenti selezionati")
    def abilita_commenti(self, request, queryset):
        updated = queryset.update(is_disabled=False)
        self.message_user(request, f"{updated} commenti abilitati.")


@admin.register(VideoLike)
class VideoLikeAdmin(admin.ModelAdmin):
    list_display = ("user", "video", "created_at")
    search_fields = ("user__username", "video__title")
    autocomplete_fields = ["user", "video"]


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ("user", "comment", "created_at")
    search_fields = ("user__username",)
    autocomplete_fields = ["user", "comment"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "sender", "type", "is_read", "created_at")
    list_filter = ("type", "is_read")
    search_fields = ("recipient__username", "sender__username")
    autocomplete_fields = ["recipient", "sender", "video", "comment", "contest"]
    readonly_fields = ("created_at",)


@admin.register(Bracket)
class BracketAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "status",
        "max_participants",
        "current_round",
        "created_by",
        "created_at",
    ]
    list_filter = ["status"]
    search_fields = ["name"]
    autocomplete_fields = ["created_by"]
    readonly_fields = ["created_at"]
    actions = ["start_bracket"]

    @admin.action(description="Avvia torneo (genera matchup)")
    def start_bracket(self, request, queryset):
        from django.contrib import messages
        from django.core.exceptions import ValidationError

        from cs_clips.utils.bracket_logic import generate_bracket

        started = 0
        errors = []
        for bracket in queryset.filter(status=Bracket.Status.REGISTRATION):
            try:
                generate_bracket(bracket)
                started += 1
            except ValidationError as e:
                errors.append(f"{bracket.name}: {e.message}")
        if started:
            self.message_user(request, f"{started} tornei avviati.")
        if errors:
            self.message_user(
                request,
                "Errori: " + "; ".join(errors),
                messages.ERROR,
            )


@admin.register(ContestEntry)
class ContestEntryAdmin(admin.ModelAdmin):
    list_display = ["bracket", "user", "video", "created_at"]
    list_filter = ["bracket"]
    search_fields = ["user__username", "video__title"]
    autocomplete_fields = ["bracket", "user", "video"]


@admin.register(Matchup)
class MatchupAdmin(admin.ModelAdmin):
    list_display = [
        "bracket",
        "round_number",
        "position",
        "entry_1",
        "entry_2",
        "winner",
        "is_completed",
    ]
    list_filter = ["bracket", "round_number", "is_completed"]
    search_fields = ["bracket__name"]


@admin.register(MatchupVote)
class MatchupVoteAdmin(admin.ModelAdmin):
    list_display = ["matchup", "user", "entry", "value", "created_at"]
    list_filter = ["value", "matchup__bracket"]
    search_fields = ["user__username"]
    autocomplete_fields = ["matchup", "user", "entry"]
    readonly_fields = ["created_at"]


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ("name", "tag", "start_date", "end_date", "is_closed", "winner")
    list_filter = ("tag", "is_closed")
    search_fields = ("name",)
    autocomplete_fields = ["winner"]
    readonly_fields = ("closed_at",)
    date_hierarchy = "start_date"
    actions = ["chiudi_contest"]

    @admin.action(description="Chiudi contest selezionati")
    def chiudi_contest(self, request, queryset):
        updated = queryset.filter(is_closed=False).update(
            is_closed=True, closed_at=timezone.now()
        )
        self.message_user(request, f"{updated} contest chiusi.")

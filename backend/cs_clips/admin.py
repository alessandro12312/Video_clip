from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone

from cs_clips.models import Comment, Contest, Rating, User, Video


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
    list_display = ("title", "uploader", "tag", "views", "created_at", "contest")
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

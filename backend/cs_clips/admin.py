from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Video, Rating, Comment, Contest, VideoLike, CommentLike, Notification

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Visualizza questi campi nella lista utenti
    list_display = ('username', 'email', 'is_staff', 'is_superuser', 'role')

    def role(self, obj):
        if obj.is_superuser:
            return 'admin'
        groups = obj.groups.all()
        return groups[0].name if groups else '-'
    role.short_description = 'Ruolo'

    readonly_fields = ['followers_list', 'following_list']

    def followers_list(self, obj):
        return ", ".join(u.username for u in obj.followers.all())

    def following_list(self, obj):
        return ", ".join(u.username for u in obj.following.all())


admin.site.register(Video)
admin.site.register(Rating)
admin.site.register(Comment)
admin.site.register(Contest)
admin.site.register(VideoLike)
admin.site.register(CommentLike)
admin.site.register(Notification)

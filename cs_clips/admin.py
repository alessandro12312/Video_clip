from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Video, Rating, Comment

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

admin.site.register(Video)
admin.site.register(Rating)
admin.site.register(Comment)

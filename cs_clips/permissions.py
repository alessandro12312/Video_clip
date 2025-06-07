from rest_framework.permissions import BasePermission, SAFE_METHODS

# Autorizzazioni basate su gruppi: 'user', 'toconfirm', 'admin' (superuser).
class RoleBasedPermission(BasePermission):
    """
    Permission basata sui ruoli:
    - Gli utenti 'user' possono leggere, creare, aggiornare e cancellare SOLO i propri contenuti.
    - Gli utenti 'toconfirm' possono solo leggere.
    - Gli admin (superuser) possono fare tutto.
    """
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        if request.user.groups.filter(name='toconfirm').exists():
            return request.method in SAFE_METHODS

        if request.user.groups.filter(name='user').exists():
            return request.method in SAFE_METHODS or request.method in ['POST', 'PUT', 'PATCH', 'DELETE']

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if request.user.groups.filter(name='toconfirm').exists():
            return request.method in SAFE_METHODS

        if request.user.groups.filter(name='user').exists():
            if request.method in SAFE_METHODS:
                return True
            # Gli utenti possono modificare solo i propri contenuti
            return obj.uploader == request.user

        return False

from rest_framework.permissions import BasePermission, SAFE_METHODS

#TODO controlla bene i gruppi e i permessi come funzionano in Django
class RoleBasedPermission(BasePermission):
    """
    Permission basata sui ruoli:
    - Gli utenti 'user' possono eliminare solo i propri contenuti.
    - Gli utenti 'toconfirm' possono solo leggere.
    - Gli admin possono fare tutto.
    """
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        # 'toconfirm' può solo leggere
        if request.user.groups.filter(name='toconfirm').exists():
            return request.method in SAFE_METHODS

        # 'user' può fare tutto (create, update, delete)
        if request.user.groups.filter(name='user').exists():

            return True

        # Se non appartiene a nessun gruppo, nega l'accesso
        return False
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        # Gli 'user' possono fare tutto, ma eliminare solo i propri contenuti
        if request.user.groups.filter(name='user').exists():
            if request.method == 'DELETE':
                return obj.user == request.user
            return True

        # 'toconfirm' solo lettura
        if request.user.groups.filter(name='toconfirm').exists():
            return request.method in SAFE_METHODS

        return False
    
#TODO crea così le classi di permessi per ogni gruppo (devi aggiungere "permission_classes=[NomeClasse]" nei viewset)
class OnlyUsersPermission(BasePermission):
    """
    Permette l'accesso solo a utenti del gruppo 'user' o admin.
    """
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (
            user.is_superuser or user.groups.filter(name='user').exists()
        )

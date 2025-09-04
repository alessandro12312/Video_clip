from django.apps import AppConfig

class CsClipsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cs_clips'

    def ready(self):
        from . import scheduler
        scheduler.start()

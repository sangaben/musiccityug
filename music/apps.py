# music/apps.py
from django.apps import AppConfig

class MusicConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'music'
    verbose_name = 'Music Library'
    
    def ready(self):
        import music.signals
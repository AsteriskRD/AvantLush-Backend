from django.apps import AppConfig

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'avantlush_backend.api'

    def ready(self):  
        import avantlush_backend.api.signals  
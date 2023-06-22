from django.apps import AppConfig


class AntragstoolConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Antragstool'
    
    def ready(self):
        import Antragstool.mails

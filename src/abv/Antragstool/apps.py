from django.apps import AppConfig


class AntragstoolConfig(AppConfig):
    """Damit das Tool einen Befehl zum startn hat."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Antragstool'
    
    def ready(self):
        import Antragstool.mails

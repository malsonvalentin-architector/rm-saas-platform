from django.apps import AppConfig


class DataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data'
    
    def ready(self):
        """
        Initialization when Django starts.
        
        NOTE: Enhanced Emulator is now running as a separate Railway service.
        No need to start it from Django anymore.
        """
        pass

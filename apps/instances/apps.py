"""
Instances app configuration
"""
from django.apps import AppConfig


class InstancesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.instances'
    
    def ready(self):
        """
        Import signals when the app is ready
        """
        import apps.instances.signals


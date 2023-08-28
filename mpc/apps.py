from django.apps import AppConfig


class MpcConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mpc'

    def ready(self):
        from .cache import get_cached_all_jurisdicionadas

        get_cached_all_jurisdicionadas()

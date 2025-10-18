from django.apps import AppConfig


class SampleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.sample'

    def ready(self):
        try:
            import apps.sample.signals  # noqa: F401
        except ImportError:
            pass

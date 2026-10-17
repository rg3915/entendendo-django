from django.apps import AppConfig


class CfpConfig(AppConfig):
    name = 'cfp'

    def ready(self):
        from . import schema  # noqa: F401  registra a extensão do drf-spectacular

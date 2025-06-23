from django.apps import AppConfig


class HatsConfig(AppConfig):
    name = "apps.hats"

    def ready(self):
        import apps.hats.signals  # noqa

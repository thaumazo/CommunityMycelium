from django.apps import AppConfig


class MaladaptivesConfig(AppConfig):
    name = "apps.maladaptives"

    def ready(self):
        import apps.maladaptives.signals  # noqa

from django.apps import AppConfig


class MapitalsConfig(AppConfig):
    name = "apps.capitals"

    def ready(self):
        import apps.capitals.signals  # noqa

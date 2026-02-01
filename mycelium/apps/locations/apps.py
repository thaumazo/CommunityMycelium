from django.apps import AppConfig


class LocationsConfig(AppConfig):
    name = "apps.locations"

    def ready(self):
        import apps.locations.signals  # noqa

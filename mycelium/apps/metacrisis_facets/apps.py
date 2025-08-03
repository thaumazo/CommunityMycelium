from django.apps import AppConfig


class Metacrisis_facetsConfig(AppConfig):
    name = "apps.metacrisis_facets"

    def ready(self):
        import apps.metacrisis_facets.signals  # noqa

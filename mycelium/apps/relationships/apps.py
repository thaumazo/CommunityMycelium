from django.apps import AppConfig


class RelationshipsConfig(AppConfig):
    name = "apps.relationships"

    def ready(self):
        import apps.relationships.signals  # noqa

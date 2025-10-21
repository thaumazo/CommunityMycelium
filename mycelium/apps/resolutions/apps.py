from django.apps import AppConfig


class ResolutionsConfig(AppConfig):
    name = "apps.resolutions"

    def ready(self):
        import apps.resolutions.signals  # noqa

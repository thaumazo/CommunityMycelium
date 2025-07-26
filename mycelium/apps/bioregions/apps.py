from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    name = "apps.bioregions"

    def ready(self):
        import apps.bioregions.signals  # noqa

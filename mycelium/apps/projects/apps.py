from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    name = "apps.projects"

    def ready(self):
        import apps.projects.signals  # noqa

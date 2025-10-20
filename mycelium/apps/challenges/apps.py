from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    name = "apps.challenges"

    def ready(self):
        import apps.challenges.signals  # noqa

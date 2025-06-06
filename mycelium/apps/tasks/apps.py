from django.apps import AppConfig


class TasksConfig(AppConfig):
    name = "apps.tasks"

    def ready(self):
        import apps.tasks.signals  # noqa

from django.apps import AppConfig


class MeetingsConfig(AppConfig):
    name = "apps.meetings"

    def ready(self):
        import apps.meetings.signals  # noqa

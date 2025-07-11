from django.apps import AppConfig


class CommunitiesConfig(AppConfig):
    name = "apps.communities"

    def ready(self):
        import apps.communities.signals  # noqa

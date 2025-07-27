from django.apps import AppConfig


class SocialrolesConfig(AppConfig):
    name = "apps.socialroles"

    def ready(self):
        import apps.socialroles.signals  # noqa

from django.apps import AppConfig


class AgreementsConfig(AppConfig):
    name = "apps.agreements"

    def ready(self):
        import apps.agreements.signals  # noqa

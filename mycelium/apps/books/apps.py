from django.apps import AppConfig


class BooksConfig(AppConfig):
    name = "apps.books"

    def ready(self):
        import apps.books.signals  # noqa

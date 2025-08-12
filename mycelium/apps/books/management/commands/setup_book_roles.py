from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.communities.models import Book
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Sets up book-specific roles and permissions"

    def handle(self, *args, **options):
        # Create book-specific groups
        book_admin_group, _ = Group.objects.get_or_create(name="Books Admin")
        book_editor_group, _ = Group.objects.get_or_create(name="Books Editor")
        book_viewer_group, _ = Group.objects.get_or_create(name="Books Viewer")

        # Get content type for Book model
        book_content_type = ContentType.objects.get_for_model(Book)

        # Get all permissions for Book model
        book_permissions = Permission.objects.filter(
            content_type=book_content_type
        )

        # Books admin group gets all permissions for agreements
        books_admin_permissions = book_permissions.filter(
            codename__in=[
                "add_book",
                "change_book",
                "delete_book",
                "view_book",
                "delegate_book",
            ]
        )
        books_admin_group.permissions.set(books_admin_permissions)

        # Books editor group gets view_agreement permission
        books_editor_permissions = book_permissions.filter(
            codename__in=[
                "add_book",
                "view_book",
            ]
        )
        books_editor_group.permissions.set(books_editor_permissions)

        # Books viewer group gets view_book permission
        books_viewer_permissions = book_permissions.filter(
            codename__in=[
                "view_book",
            ]
        )
        books_viewer_group.permissions.set(books_viewer_permissions)

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully set up book-specific roles and permissions"
            )
        )

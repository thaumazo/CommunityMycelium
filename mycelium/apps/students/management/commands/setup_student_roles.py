from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.communities.models import Student
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Sets up student-specific roles and permissions"

    def handle(self, *args, **options):
        # Create student-specific groups
        student_admin_group, _ = Group.objects.get_or_create(name="Students Admin")
        student_editor_group, _ = Group.objects.get_or_create(name="Students Editor")
        student_viewer_group, _ = Group.objects.get_or_create(name="Students Viewer")

        # Get content type for Student model
        student_content_type = ContentType.objects.get_for_model(Student)

        # Get all permissions for Student model
        student_permissions = Permission.objects.filter(
            content_type=student_content_type
        )

        # Students admin group gets all permissions for agreements
        students_admin_permissions = student_permissions.filter(
            codename__in=[
                "add_student",
                "change_student",
                "delete_student",
                "view_student",
                "delegate_student",
            ]
        )
        students_admin_group.permissions.set(students_admin_permissions)

        # Students editor group gets view_agreement permission
        students_editor_permissions = student_permissions.filter(
            codename__in=[
                "add_student",
                "view_student",
            ]
        )
        students_editor_group.permissions.set(students_editor_permissions)

        # Students viewer group gets view_student permission
        students_viewer_permissions = student_permissions.filter(
            codename__in=[
                "view_student",
            ]
        )
        students_viewer_group.permissions.set(students_viewer_permissions)

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully set up student-specific roles and permissions"
            )
        )

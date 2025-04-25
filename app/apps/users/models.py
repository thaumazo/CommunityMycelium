from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    def is_admin(self):
        return self.groups.filter(name="Admin").exists()

    def is_editor(self):
        return self.groups.filter(name="Editor").exists()

    def is_viewer(self):
        return self.groups.filter(name="Viewer").exists()

    @property
    def role(self):
        if self.is_admin():
            return "Admin"
        elif self.is_editor():
            return "Editor"
        elif self.is_viewer():
            return "Viewer"
        return "No Role"

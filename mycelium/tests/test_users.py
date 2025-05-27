import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.test import TestCase

from mycelium.apps.users.forms import (
    LoginForm,
    RegisterForm,
    UserForm,
    UserPermissionForm,
)

User = get_user_model()


@pytest.mark.django_db
class TestUserModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            full_name="Test User",
        )
        self.admin_group = Group.objects.create(name="Admin")

    def test_user_creation(self):
        """Test that a user can be created with required fields."""
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertEqual(self.user.full_name, "Test User")
        self.assertTrue(self.user.check_password("testpass123"))

    def test_get_full_name(self):
        """Test the get_full_name method."""
        self.assertEqual(self.user.get_full_name(), "Test User")

    def test_get_short_name(self):
        """Test the get_short_name method."""
        self.assertEqual(self.user.get_short_name(), "Test User")

    def test_is_admin(self):
        """Test the is_admin method."""
        self.assertFalse(self.user.is_admin())
        self.user.groups.add(self.admin_group)
        self.assertTrue(self.user.is_admin())


@pytest.mark.django_db
class TestRegisterForm(TestCase):
    def test_register_form_valid_data(self):
        """Test register form with valid data."""
        form_data = {
            "username": "newuser",
            "email": "new@example.com",
            "full_name": "New User",
            "password": "testpass123",
            "confirm_password": "testpass123",
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, "newuser")
        self.assertEqual(user.email, "new@example.com")
        self.assertEqual(user.full_name, "New User")
        self.assertTrue(user.check_password("testpass123"))

    def test_register_form_password_mismatch(self):
        """Test register form with mismatched passwords."""
        form_data = {
            "username": "newuser",
            "email": "new@example.com",
            "full_name": "New User",
            "password": "testpass123",
            "confirm_password": "differentpass",
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("Passwords", str(form.errors))

@pytest.mark.django_db
class TestUserPermissionForm(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            full_name="Test User",
        )
        self.admin_group = Group.objects.create(name="Admin")
        self.user_group = Group.objects.create(name="User")

    def test_user_permission_form_initial(self):
        """Test user permission form initial values."""
        self.user.groups.add(self.user_group)
        form = UserPermissionForm(user=self.user)
        self.assertEqual(list(form.fields["groups"].initial), [self.user_group])

    def test_user_permission_form_admin_override(self):
        """Test that selecting Admin group removes other groups."""
        form_data = {"groups": [self.admin_group.id, self.user_group.id]}
        form = UserPermissionForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
        cleaned_data = form.clean()
        self.assertEqual(list(cleaned_data["groups"]), [self.admin_group]) 
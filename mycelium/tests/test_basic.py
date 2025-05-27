import pytest
from django.test import TestCase

def test_basic():
    """Basic test to verify pytest is working."""
    assert True

class BasicTestCase(TestCase):
    """Basic Django test case to verify Django test setup."""
    
    def test_django_setup(self):
        """Test that Django test setup is working."""
        self.assertTrue(True) 
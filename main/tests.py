"""Module for creating tests"""
from django.test import TestCase


class TestClass(TestCase):
    """Main class for testing"""

    def test_something_that_will_pass(self):
        """Test that always will be true"""
        self.assertTrue(1 + 1 == 2)

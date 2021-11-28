"""Module for creating tests"""
import os
from django.test import TestCase
from dotenv import load_dotenv

load_dotenv()


class TestClass(TestCase):
    """Main class for testing"""

    def test_something_that_will_pass(self):
        """Test that always will be true"""
        print(os.environ['TEST'])
        self.assertTrue(1 + 1 == 2)

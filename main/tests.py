"""Module for creating tests"""
import os

from asgiref.sync import async_to_sync, sync_to_async
from django.test import TestCase
from dotenv import load_dotenv

from main.helpers import get_apis
from main.models import Config
from main.src.get_all.friends import get_friends

load_dotenv()


class TestClass(TestCase):
    """Main class for testing"""

    async def test_something_that_will_pass(self):
        """Test that always will be true"""
        config = await sync_to_async(Config.objects.create)(chain='3')
        tokens = [os.environ['TOKEN1'], os.environ['TOKEN2'], os.environ['TOKEN3']]
        apis = await get_apis(tokens)
        friends = await get_friends(64560019, apis, config)
        self.assertEqual(2, len(friends))

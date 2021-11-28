"""Module for creating tests"""
import os

from django.test import TestCase
from dotenv import load_dotenv

from main.helpers import get_apis
from main.models import Config
from main.src.get_all.albums import get_albums
from main.src.get_all.friends import get_friends
from main.src.get_all.groups import get_groups
from main.src.get_all.members import get_members
from main.src.get_all.photos import get_photos
from main.src.get_all.posts import get_posts
from main.src.get_all.users import get_users

load_dotenv()


class GetAllTests(TestCase):
    """Testing get_all funcs"""
    config = Config.objects.create(limit_groups=100, hard_limit_groups=100,
                                   limit_members=10000, hard_limit_members=100000,
                                   remaining_chain='4', limit_photos=100, hard_limit_photos=100,
                                   limit_posts=10000, hard_limit_posts=100000)
    tokens = [os.environ['TOKEN1'], os.environ['TOKEN2'], os.environ['TOKEN3']]
    testing_user = 64560019
    testing_group = 29229881

    async def test_friends(self):
        """Testing get_all.friends"""
        apis = await get_apis(self.tokens)
        friends = await get_friends(self.testing_user, apis, self.config)
        self.assertEqual(2, len(friends))

    async def test_groups(self):
        """Testing get_all.groups"""
        apis = await get_apis(self.tokens)
        groups = await get_groups(self.testing_user, apis, self.config)
        self.assertEqual(3, len(groups))

    async def test_members(self):
        """Testing get_all.members"""
        apis = await get_apis(self.tokens)
        members = await get_members(self.testing_group, apis, self.config)
        self.assertEqual(10000, len(members))

    async def test_albums_and_photos(self):
        """Testing get_all.photos"""
        apis = await get_apis(self.tokens)
        albums = await get_albums(self.testing_user, apis, self.config)
        self.assertEqual(4, len(albums))
        photos = await get_photos(self.testing_user, albums, apis, self.config)
        self.assertEqual(8, len(photos))

    async def test_posts(self):
        """Testing get_all.posts"""
        apis = await get_apis(self.tokens)
        posts = await get_posts(self.testing_user, apis, self.config)
        self.assertEqual(5, len(posts))

    async def test_users(self):
        """Testing get_all.users"""
        apis = await get_apis(self.tokens)
        user = await get_users([self.testing_user], False, apis, self.config, 'bdate, city, status')
        city = user[0]['city']['title']
        status = user[0]['status']
        bdate = user[0]['bdate']
        self.assertEqual('Уфа', city)
        self.assertEqual('no status', status)
        self.assertEqual('5.2.1902', bdate)

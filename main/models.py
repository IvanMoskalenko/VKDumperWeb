"""Module with existing models in app"""
import json

from asgiref.sync import sync_to_async
from django.db import models

from main.helpers import get_apis, current_date_and_time, get_api
from main.src.chains import ids_users_ids, ids_groups_members_ids, ids_friends_ids, ids_albums_photos_ids, ids_posts_ids


class Token(models.Model):
    """Representation of VK API access-token"""
    token = models.CharField('Token', max_length=85)

    def __str__(self):
        return self.token


class Config(models.Model):
    """Implementation of config providing information for running task"""
    chain = models.CharField(max_length=100)
    ids = models.TextField(default='')
    photo_type = models.CharField(max_length=1, default='S')
    fields = models.TextField(default='')
    limit_groups = models.IntegerField(default=0)
    limit_members = models.IntegerField(default=0)
    limit_photos = models.IntegerField(default=0)
    limit_posts = models.IntegerField(default=0)
    hard_limit_groups = models.IntegerField(default=0)
    hard_limit_members = models.IntegerField(default=0)
    hard_limit_photos = models.IntegerField(default=0)
    hard_limit_posts = models.IntegerField(default=0)
    interpreted_chain = models.TextField(default='')
    remaining_chain = models.TextField(default='')
    progress = models.FloatField(default=0)
    is_need_to_reload_tokens = models.BooleanField(default=False)
    current_tokens = models.TextField(default='')
    original_chain = models.TextField(default='')
    errors = models.TextField(default='')

    async def start_executing(self, tokens):
        """Starts executing of task with config information"""
        self.current_tokens = json.dumps(tokens)
        await sync_to_async(self.save)()
        remaining_progress = 100 - self.progress
        progress_chunk = remaining_progress / len(self.chain)
        apis = await get_apis(tokens)
        counter = len(self.original_chain) - len(self.chain)
        datetime = current_date_and_time()
        for link in self.chain:
            match link:
                case "1":
                    ids = await ids_users_ids(counter, apis, progress_chunk, self, datetime)
                case "2":
                    ids = await ids_groups_members_ids(apis, progress_chunk, self)
                case "3":
                    ids = await ids_friends_ids(apis, progress_chunk, self)
                case "4" | "5":
                    ids = await ids_albums_photos_ids(apis, counter, progress_chunk, self, datetime)
                case _:
                    ids = await ids_posts_ids(apis, counter, progress_chunk, self, datetime)
            counter += 1
            await sync_to_async(self.refresh_from_db)()
            self.remaining_chain = self.remaining_chain[1:]
            self.ids = json.dumps(ids)
            await sync_to_async(self.save)()
        await sync_to_async(self.delete)()

    async def reload_tokens(self, apis):
        """Reload available tokens"""
        json_dec = json.decoder.JSONDecoder()
        tokens = [await sync_to_async(token.get)('token')
                  for token in await sync_to_async(list)(Token.objects.values())]
        previous_tokens = json_dec.decode(self.current_tokens)
        new_tokens = [token for token in tokens if token not in previous_tokens]
        api_list = [get_api(token) for token in new_tokens]
        self.current_tokens = json.dumps(previous_tokens + new_tokens)
        self.is_need_to_reload_tokens = False
        await sync_to_async(self.save)()
        for api in api_list:
            await apis.put(api)

    def need_to_reload_tokens(self):
        """Notifies about the need of reloading tokens"""
        self.is_need_to_reload_tokens = True
        self.save()

    async def update_errors(self, error):
        """Updates the text field about errors that have occurred"""
        self.errors += error + '\n'
        await sync_to_async(self.save)()

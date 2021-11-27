import json

from asgiref.sync import sync_to_async
from django.db import models

from Main.helpers import get_settings, current_date_and_time, get_api
from Main.src.chains import ids_users_ids, ids_groups_members_ids, ids_friends_ids, ids_albums_photos_ids, \
    ids_albums_photos_download_ids, ids_posts_ids


class Token(models.Model):
    token = models.CharField('Token', max_length=85)

    def __str__(self):
        return self.token


class Config(models.Model):
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
        self.current_tokens = json.dumps(tokens)
        await sync_to_async(self.save)()
        json_dec = json.decoder.JSONDecoder()
        ids = json_dec.decode(self.ids)
        remaining_progress = 100 - self.progress
        progress_chunk = remaining_progress / len(self.chain)
        apis = await get_settings(tokens)
        c = len(self.original_chain) - len(self.chain)
        datetime = current_date_and_time()
        for link in self.chain:
            if link == "1":
                ids = await ids_users_ids(ids, c, apis, progress_chunk, self, datetime)
            if link == "2":
                ids = await ids_groups_members_ids(ids, apis, progress_chunk, self)
            if link == "3":
                ids = await ids_friends_ids(ids, apis, progress_chunk, self)
            if link == "4":
                ids = await ids_albums_photos_ids(ids, apis, c, progress_chunk, self, datetime)
            if link == "5":
                ids = await \
                    ids_albums_photos_download_ids(ids, apis, c, progress_chunk, self, datetime)
            if link == "6":
                ids = await ids_posts_ids(ids, apis, c, progress_chunk, self, datetime)
            c += 1
            await sync_to_async(self.refresh_from_db)()
            self.remaining_chain = self.remaining_chain[1:]
            self.ids = json.dumps(ids)
            await sync_to_async(self.save)()
        await sync_to_async(self.delete)()

    async def reload_tokens(self, apis):
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
        self.is_need_to_reload_tokens = True
        self.save()

    async def update_errors(self, error):
        self.errors += error + '\n'
        await sync_to_async(self.save)()


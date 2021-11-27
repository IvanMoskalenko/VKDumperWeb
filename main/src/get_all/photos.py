"""Module for getting all user's photos"""
import math
import os
import queue

import aiohttp
from asgiref.sync import sync_to_async
from vkbottle import VKAPIError

from main.src.get_all.helpers \
    import current_time, put_with_timeout, photos_downloader, saver, save_on_server, vk_error_handler


async def get_user_photos_requests(apis, user_id, hard_limit, limit, config):
    """Func returns requests for getting all photos that the user is marked on"""
    api = None
    api_requests = queue.Queue()
    while True:
        try:
            api = await apis.get()
            count_response = await api.request("photos.getUserPhotos",
                                               {'user_id': user_id, 'count': 0})
            await put_with_timeout(apis, api, 0.34)
            if count_response['response']['count'] <= int(hard_limit):
                photos_range = math.ceil(count_response['response']['count'] / 1000)
                limit_range = math.ceil(int(limit) / 1000)
                for i in range(min(photos_range, limit_range)):
                    api_requests.put(("photos.getUserPhotos", {'user_id': user_id,
                                                               'offset': i * 1000,
                                                               'count': 1000}))
            return api_requests
        except (aiohttp.ClientOSError,
                aiohttp.ServerDisconnectedError) as error:
            await put_with_timeout(apis, api, 0.34)
            await config.update_errors(f'{current_time()} {str(error).rstrip()}')
        except await sync_to_async(VKAPIError)() as error:
            if error.code not in (5, 29):
                await put_with_timeout(apis, api, 0.34)
                await config.update_errors(f'{current_time()} {error.error_description}')
                return api_requests
            await vk_error_handler(error, apis, api, config)


async def get_album_photos_requests(apis, user_id, album_id, hard_limit, limit, config):
    """Func returns requests for getting all photos from one album"""
    api = None
    api_requests = queue.Queue()
    while True:
        try:
            api = await apis.get()
            count_response = await api.request("photos.get",
                                               {'owner_id': user_id, 'album_id': album_id,
                                                'count': 0})
            await put_with_timeout(apis, api, 0.34)
            if count_response['response']['count'] <= int(hard_limit):
                photos_range = math.ceil(count_response['response']['count'] / 1000)
                limit_range = math.ceil(int(limit) / 1000)
                for i in range(min(photos_range, limit_range)):
                    api_requests.put(("photos.get", {'owner_id': user_id,
                                                     'offset': i * 1000,
                                                     'album_id': album_id,
                                                     'count': 1000}))
            return api_requests
        except (aiohttp.ClientOSError,
                aiohttp.ServerDisconnectedError) as error:
            await put_with_timeout(apis, api, 0.34)
            await config.update_errors(f'{current_time()} {str(error).rstrip()}')
        except await sync_to_async(VKAPIError)() as error:
            if error.code not in (5, 29):
                await put_with_timeout(apis, api, 0.34)
                await config.update_errors(f'{current_time()} {error.error_description}')
                return api_requests
            await vk_error_handler(error, apis, api, config)


async def get_all_photos_from_one_album(user_id, album_id, limit, path, is_download, apis, hard_limit, config, photo_type='S'):
    """Func gets all photos from one album"""
    api = None
    photos_list = []
    if album_id == -9000:
        api_requests = await get_user_photos_requests(apis, user_id, hard_limit, limit, config)
    else:
        api_requests = await get_album_photos_requests(apis, user_id, album_id, hard_limit, limit, config)
    while True:
        try:
            if album_id == -9000:
                while not api_requests.empty():
                    fst, snd = api_requests.queue[0]
                    api = await apis.get()
                    response = await api.request(fst, snd)
                    api_requests.get()
                    await put_with_timeout(apis, api, 0.34)
                    for item in response['response']['items']:
                        item['album_id'] = -9000
                        item['owner_id'] = user_id
                        item.pop('access_key', None)
                        item.pop('user_id', None)
                    photos_downloader(is_download, response, path, user_id, photo_type)
                    photos_list.extend(response['response']['items'])
            else:
                while not api_requests.empty():
                    fst, snd = api_requests.queue[0]
                    api = await apis.get()
                    response = await api.request(fst, snd)
                    api_requests.get()
                    await put_with_timeout(apis, api, 0.34)
                    photos_downloader(is_download, response, path, user_id, photo_type)
                    photos_list.extend(response['response']['items'])
            return photos_list
        except (aiohttp.ClientOSError,
                aiohttp.ServerDisconnectedError) as error:
            await put_with_timeout(apis, api, 0.34)
            await config.update_errors(f'{current_time()} {str(error).rstrip()}')
        except await sync_to_async(VKAPIError)() as error:
            if error.code not in (5, 29):
                await put_with_timeout(apis, api, 0.34)
                await config.update_errors(f'{current_time()} {error.error_description}')
                return []
            await vk_error_handler(error, apis, api, config)


async def get_photos(user_id, albums_ids, limit, path, is_download, apis, hard_limit, config, photo_type='S'):
    """Func gets all user's photos"""
    path_file = os.path.join(path, f"id{user_id}.csv")
    photos_list = []

    for album in albums_ids:
        album_photos_list = \
            await get_all_photos_from_one_album(user_id, album, limit, path, is_download, apis, hard_limit, config, photo_type)
        photos_list.extend(album_photos_list)
    saver(photos_list, path_file)
    save_on_server(path_file)
    os.remove(path_file)

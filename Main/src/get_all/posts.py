import math
import os
import queue

import aiohttp
from asgiref.sync import sync_to_async
from vkbottle import VKAPIError

from Main.src.get_all.helpers import \
    current_time, put_with_timeout, saver, save_on_server, vk_error_handler


async def get_posts_request(apis, user_id, hard_limit, limit, config):
    api = None
    api_requests = queue.Queue()
    while True:
        try:
            api = await apis.get()
            count_response = await api.request("wall.get", {'owner_id': user_id, 'count': 0})
            await put_with_timeout(apis, api, 0.34)
            if 0 < count_response['response']['count'] < int(hard_limit):
                posts_range = math.ceil((count_response['response']['count'] / 100))
                limit_range = math.ceil((int(limit) / 100))
                for i in range(min(posts_range, limit_range)):
                    api_requests.put(("wall.get", {'owner_id': user_id, 'count': 100, 'offset': i * 100}))
            return api_requests
        except (aiohttp.ClientOSError,
                aiohttp.ServerDisconnectedError) as error:
            await put_with_timeout(apis, api, 0.34)
            await config.update_errors(f'{current_time()} {str(error).rstrip()}')
        except await sync_to_async(VKAPIError)() as error:
            if error.code != 5 and error.code != 29:
                await put_with_timeout(apis, api, 0.34)
                await config.update_errors(f'{current_time()} {error.error_description}')
                return api_requests
            else:
                await vk_error_handler(error, apis, api, config)


async def get_posts(user_id, limit, path, apis, hard_limit, config):
    api = None
    posts_list = []
    api_requests = await get_posts_request(apis, user_id, hard_limit, limit, config)
    while True:
        try:
            while not api_requests.empty():
                fst, snd = api_requests.queue[0]
                api = await apis.get()
                response = await api.request(fst, snd)
                api_requests.get()
                await put_with_timeout(apis, api, 0.34)
                posts_list.extend(response['response']['items'])
            saver(posts_list, path)
            save_on_server(path)
            os.remove(path)
            break
        except (aiohttp.ClientOSError,
                aiohttp.ServerDisconnectedError) as error:
            await put_with_timeout(apis, api, 0.34)
            await config.update_errors(f'{current_time()} {str(error).rstrip()}')
        except await sync_to_async(VKAPIError)() as error:
            if error.code != 5 and error.code != 29:
                await put_with_timeout(apis, api, 0.34)
                await config.update_errors(f'{current_time()} {error.error_description}')
                break
            else:
                await vk_error_handler(error, apis, api, config)
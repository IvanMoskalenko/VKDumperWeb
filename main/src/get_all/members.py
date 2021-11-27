"""Module for getting all members from one group"""
import math
import queue

import aiohttp
from asgiref.sync import sync_to_async
from vkbottle import VKAPIError

from main.src.get_all.helpers import \
    current_time, put_with_timeout, vk_error_handler


async def get_members_requests(group_id, limit, apis, hard_limit, config):
    """Func returns requests for getting members"""
    api = None
    api_requests = queue.Queue()
    while True:
        try:
            api = await apis.get()
            count_response = await api.request("groups.getMembers",
                                               {'group_id': group_id, 'count': 0})
            await put_with_timeout(apis, api, 0.34)
            if count_response['response']['count'] > int(hard_limit):
                return api_requests
            members_range = math.ceil(count_response['response']['count'] / 1000)
            limit_range = math.ceil(int(limit) / 1000)
            for i in range(min(members_range, limit_range)):
                api_requests.put(("groups.getMembers",
                                  {'group_id': group_id, 'offset': i * 1000}))
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


async def get_members(group_id, limit, apis, hard_limit, config):
    """Func gets all members"""
    api = None
    api_requests = await get_members_requests(group_id, limit, apis, hard_limit, config)
    list_of_members = []
    while True:
        try:
            while not api_requests.empty():
                fst, snd = api_requests.queue[0]
                api = await apis.get()
                response = await api.request(fst, snd)
                api_requests.get()
                await put_with_timeout(apis, api, 0.34)
                list_of_members.extend(response['response']['items'])
            return list_of_members
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

"""Module for getting all user's groups"""
import math
import aiohttp
from asgiref.sync import sync_to_async
from vkbottle import VKAPIError

from main.src.get_all.helpers import \
    current_time, put_with_timeout, vk_error_handler


async def get_groups(user_id, apis, config):
    """Func gets all groups from one user"""
    api = None
    while True:
        try:
            api = await apis.get()
            count_response = await api.request("groups.get", {'user_id': user_id, 'count': 1})
            await put_with_timeout(apis, api, 0.34)
            list_of_groups = []
            hard_limit = config.hard_limit_groups
            limit = config.limit_groups
            if count_response['response']['count'] > int(hard_limit):
                return list_of_groups
            groups_range = math.ceil(count_response['response']['count'] / 1000)
            limit_range = math.ceil(int(limit) / 1000)
            api = await apis.get()
            for i in range(min(groups_range, limit_range)):
                response = await api.request("groups.get", {'user_id': user_id, 'offset': i * 1000})
                list_of_groups.extend(response['response']['items'])
            await put_with_timeout(apis, api, 0.34)
            return list_of_groups
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

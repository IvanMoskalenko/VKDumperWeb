import asyncio
import aiohttp
from asgiref.sync import sync_to_async
from vkbottle import VKAPIError

from Main.src.get_all.helpers import \
    current_time, put_with_timeout, vk_error_handler


async def get_friends(user_id, apis, config):
    """Func gets all friends."""
    api = None
    while True:
        try:
            api = await apis.get()
            list_of_friends = await api.request("friends.get", {'user_id': user_id, 'count': 10000})
            await put_with_timeout(apis, api, 0.34)
            return list_of_friends['response']['items']
        except (aiohttp.ClientOSError,
                aiohttp.ServerDisconnectedError) as error:
            await put_with_timeout(apis, api, 0.34)
            await config.update_errors(f'{current_time()} {str(error).rstrip()}')
        except await sync_to_async(VKAPIError)() as error:
            if error.code != 5 and error.code != 29:
                await put_with_timeout(apis, api, 0.34)
                await config.update_errors(f'{current_time()} {error.error_description}')
                return []
            else:
                await vk_error_handler(error, apis, api, config)

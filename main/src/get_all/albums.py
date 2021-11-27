"""Module for getting all user's albums"""
import aiohttp
from asgiref.sync import sync_to_async
from vkbottle import VKAPIError

from main.src.get_all.helpers import \
    current_time, put_with_timeout, vk_error_handler


async def get_albums(user_id, apis, config):
    """Func gets all albums from one user"""
    api = None
    while True:
        try:
            api = await apis.get()
            response = await api.request("photos.getAlbums",
                                         {'owner_id': user_id, 'need_system': 1})
            await put_with_timeout(apis, api, 0.34)
            ids = [album['id'] for album in response['response']['items']]
            return ids
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

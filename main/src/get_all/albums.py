"""Module for getting all user's albums"""

from main.src.get_all.helpers import put_with_timeout, response_executor


async def get_albums(user_id, apis, config):
    """Func gets all albums from one user"""
    api = await apis.get()
    api_request = ("photos.getAlbums",
                   {'owner_id': user_id, 'need_system': 1})
    response = await response_executor(api_request, apis, config)
    if response is None:
        return []
    await put_with_timeout(apis, api, 0.34)
    ids = [album['id'] for album in response['response']['items']]
    return ids

"""Module for getting all user's photos"""
import math
import queue

from main.src.get_all.helpers \
    import photos_downloader, response_executor


async def get_album_photos_requests(apis, user_id, album_id, config):
    """Func returns requests for getting all photos from one album"""
    api_requests = queue.Queue()
    if album_id == -9000:
        api_request = ("photos.getUserPhotos",
                       {'user_id': user_id, 'count': 0})
    else:
        api_request = ("photos.get",
                       {'owner_id': user_id, 'album_id': album_id,
                        'count': 0})
    count_response = await response_executor(api_request, apis, config)
    if count_response is None:
        return api_requests
    hard_limit = config.hard_limit_photos
    limit = config.limit_photos
    if count_response['response']['count'] <= int(hard_limit):
        photos_range = math.ceil(count_response['response']['count'] / 1000)
        limit_range = math.ceil(int(limit) / 1000)
        for i in range(min(photos_range, limit_range)):
            if album_id == -9000:
                api_requests.put(("photos.getUserPhotos", {'user_id': user_id,
                                                           'offset': i * 1000,
                                                           'count': 1000}))
            else:
                api_requests.put(("photos.get", {'owner_id': user_id,
                                                 'offset': i * 1000,
                                                 'album_id': album_id,
                                                 'count': 1000}))
    return api_requests


async def get_all_photos_from_one_album(user_id, album_id, apis, config, path=""):
    """Func gets all photos from one album"""
    photos_list = []
    api_requests = await get_album_photos_requests(apis, user_id, album_id, config)
    while not api_requests.empty():
        api_request = api_requests.get()
        response = await response_executor(api_request, apis, config)
        if album_id == -9000:
            for item in response['response']['items']:
                item['album_id'] = -9000
                item['owner_id'] = user_id
                item.pop('access_key', None)
                item.pop('user_id', None)
        if config.remaining_chain[0] == '5':
            photos_downloader(response, path, user_id, config.photo_type)
        photos_list.extend(response['response']['items'])
    return photos_list


async def get_photos(user_id, albums_ids, apis, config, path=""):
    """Func gets all user's photos"""
    photos_list = []

    for album in albums_ids:
        album_photos_list = await get_all_photos_from_one_album(user_id, album, apis, config, path)
        photos_list.extend(album_photos_list)
    return photos_list

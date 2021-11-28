"""Module for getting all users' posts"""
import math
import queue

from main.src.get_all.helpers import response_executor


async def get_posts_request(apis, user_id, config):
    """Func returns requests for getting all posts"""
    api_requests = queue.Queue()
    api_request = ("wall.get", {'owner_id': user_id, 'count': 0})
    count_response = await response_executor(api_request, apis, config)
    if count_response is None:
        return api_requests
    hard_limit = config.hard_limit_posts
    limit = config.limit_posts
    if 0 < count_response['response']['count'] < int(hard_limit):
        posts_range = math.ceil((count_response['response']['count'] / 100))
        limit_range = math.ceil((int(limit) / 100))
        for i in range(min(posts_range, limit_range)):
            api_requests.put(("wall.get", {'owner_id': user_id, 'count': 100, 'offset': i * 100}))
    return api_requests


async def get_posts(user_id, apis, config):
    """Func gets all user's post"""
    posts_list = []
    api_requests = await get_posts_request(apis, user_id, config)
    while not api_requests.empty():
        api_request = api_requests.get()
        response = await response_executor(api_request, apis, config)
        posts_list.extend(response['response']['items'])
    return posts_list

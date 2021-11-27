"""Module for getting all user's friends"""

from main.src.get_all.helpers import response_executor


async def get_friends(user_id, apis, config):
    """Func gets all friends of one user"""
    api_request = ("friends.get", {'user_id': user_id, 'count': 10000})
    list_of_friends = await response_executor(api_request, apis, config)
    if list_of_friends is None:
        return []
    return list_of_friends['response']['items']

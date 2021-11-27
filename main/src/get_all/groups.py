"""Module for getting all user's groups"""
import math

from main.src.get_all.helpers import response_executor


async def get_groups(user_id, apis, config):
    """Func gets all groups from one user"""
    api_request = ("groups.get", {'user_id': user_id, 'count': 1})
    count_response = await response_executor(api_request, apis, config)
    list_of_groups = []
    if count_response is None:
        return list_of_groups
    hard_limit = config.hard_limit_groups
    limit = config.limit_groups
    if count_response['response']['count'] > int(hard_limit):
        return list_of_groups
    groups_range = math.ceil(count_response['response']['count'] / 1000)
    limit_range = math.ceil(int(limit) / 1000)
    for i in range(min(groups_range, limit_range)):
        api_request = ("groups.get", {'user_id': user_id, 'offset': i * 1000})
        response = await response_executor(api_request, apis, config)
        list_of_groups.extend(response['response']['items'])
    return list_of_groups

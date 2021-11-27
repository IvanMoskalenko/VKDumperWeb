"""Module for getting all members from one group"""
import math
import queue

from main.src.get_all.helpers import response_executor


async def get_members_requests(group_id, apis, config):
    """Func returns requests for getting members"""
    api_requests = queue.Queue()
    api_request = ("groups.getMembers",
                   {'group_id': group_id, 'count': 0})
    count_response = await response_executor(api_request, apis, config)
    hard_limit = config.hard_limit_members
    limit = config.limit_members
    if count_response['response']['count'] > int(hard_limit):
        return api_requests
    members_range = math.ceil(count_response['response']['count'] / 1000)
    limit_range = math.ceil(int(limit) / 1000)
    for i in range(min(members_range, limit_range)):
        api_requests.put(("groups.getMembers",
                          {'group_id': group_id, 'offset': i * 1000}))
    return api_requests


async def get_members(group_id, apis, config):
    """Func gets all members"""
    api_requests = await get_members_requests(group_id, apis, config)
    list_of_members = []
    while not api_requests.empty():
        api_request = api_requests.get()
        response = await response_executor(api_request, apis, config)
        list_of_members.extend(response['response']['items'])
    return list_of_members

"""Module for getting users' information"""
import queue

from main.src.get_all.helpers import \
    users_list_handler, response_executor


async def get_users(users_ids, is_one_by_one, apis, config, fields=''):
    """Func gets users' information with fields given"""
    list_of_users = []
    if is_one_by_one:
        user_list = users_list_handler(users_ids, 1)
    else:
        user_list = users_list_handler(users_ids, 1000)
    users_range = len(user_list)
    api_requests = queue.Queue()
    for i in range(users_range):
        api_requests.put(("users.get",
                          {"user_ids": user_list[i], "fields": fields}))
    while not api_requests.empty():
        api_request = api_requests.get()
        response = await response_executor(api_request, apis, config)
        list_of_users.extend(response['response'])

    return list_of_users

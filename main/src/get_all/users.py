import queue

import aiohttp
from asgiref.sync import sync_to_async
from vkbottle import VKAPIError

from main.src.get_all.helpers import \
    users_list_handler, current_time, put_with_timeout, vk_error_handler


async def get_users(users_ids, is_one_by_one, apis, config, fields=''):
    api = None
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
    while True:
        try:
            while not api_requests.empty():
                fst, snd = api_requests.queue[0]
                api = await apis.get()
                response = await api.request(fst, snd)
                api_requests.get()
                await put_with_timeout(apis, api, 0.34)
                list_of_users.extend(response['response'])
            break
        except (aiohttp.ClientOSError,
                aiohttp.ServerDisconnectedError) as error:
            await put_with_timeout(apis, api, 0.34)
            await config.update_errors(f'{current_time()} {str(error).rstrip()}')
        except await sync_to_async(VKAPIError)() as error:
            if error.code != 5 and error.code != 29:
                await put_with_timeout(apis, api, 0.34)
                await config.update_errors(f'{current_time()} {error.error_description}')
                break
            else:
                await vk_error_handler(error, apis, api, config)

    return list_of_users

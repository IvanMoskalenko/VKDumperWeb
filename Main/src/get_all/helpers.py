import asyncio
import csv
import os
from datetime import datetime

import boto3

from Main.src.helpers import get_required_size, save_image


def current_time():
    """Func gets current time."""
    return datetime.now().strftime('%H:%M:%S')


def users_list_handler(users_ids, chunk_size):
    """Func divides list and creates strings. Necessary for get_all.users."""

    def div_list(my_list, size):
        return [my_list[x: x + size] for x in range(0, len(my_list), size)]

    divided_list = div_list(users_ids, chunk_size)
    res_list = []
    for i in divided_list:
        res_list.append(', '.join([str(x) for x in i]))
    return res_list


def photos_downloader(is_download, response, path, user_id, photo_type):
    if is_download:
        for photo in response['response']['items']:
            path_with_new_dirs = os.path.join(
                path, str(user_id), str(photo['album_id']))
            if not os.path.isdir(path_with_new_dirs):
                os.makedirs(path_with_new_dirs)
            ready_path = os.path.join(path_with_new_dirs, f"date{photo['date']}_id{photo['id']}.jpg")
            required_size = get_required_size(photo['sizes'], photo_type)
            url = required_size['url']
            save_image(url, ready_path)
            save_on_server(ready_path)
            os.remove(ready_path)


async def put_with_timeout(apis, api, timeout):
    await asyncio.sleep(timeout)
    await apis.put(api)


def saver(items_list, path):
    """Func creates dataframe from list and saves it."""
    fieldnames = set()
    for item in items_list:
        fieldnames.update(item.keys())
    fieldnames = sorted(fieldnames)
    with open(path, 'w', encoding='utf8', newline='') as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(items_list)


def save_on_server(path_to_file):
    session = boto3.session.Session()
    s3 = session.client(
        aws_access_key_id='bjy3Jfov0IGVq3RH5yjx',
        aws_secret_access_key='cgUWI4oXkY_RqhMEgISc77hU9XJqVcyqYOJWE6uu',
        region_name='ru-central1',
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net'
    )

    s3.upload_file(path_to_file, 'datasetsvkparser', path_to_file)
    s3.upload_file(path_to_file, 'datasetsvkparser', path_to_file)


async def vk_error_handler(error, apis, api, config):
    if error.code == 5:
        await config.update_errors(f'{current_time()} {error.error_description}')
    else:
        await config.update_errors(f'{current_time()} {error.error_description}')
        asyncio.create_task(put_with_timeout(apis, api, 600))

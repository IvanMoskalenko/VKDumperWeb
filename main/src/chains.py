import os
import numpy
from asyncio import Queue
from asgiref.sync import sync_to_async
from main.src.get_all.helpers import saver, save_on_server
from main.src.helpers import limited_as_completed
from main.src.get_all.albums import get_albums
from main.src.get_all.friends import get_friends
from main.src.get_all.groups import get_groups
from main.src.get_all.members import get_members
from main.src.get_all.photos import get_photos
from main.src.get_all.posts import get_posts
from main.src.get_all.users import get_users


async def coros_executor(one_iteration, users_ids, apis, config, progress_chunk):
    if config.is_need_to_reload_tokens:
        await config.reload_tokens(apis)
    coros = (one_iteration(user_id) for user_id in users_ids)
    for coro in limited_as_completed(coros, apis.qsize()):
        await coro
        await sync_to_async(config.refresh_from_db)()
        if config.is_need_to_reload_tokens:
            await config.reload_tokens(apis)
        config.progress += (progress_chunk / len(users_ids))
        await sync_to_async(config.save)()


async def ids_users_ids(users_ids, iteration, apis: Queue, progress_chunk, config, datetime):
    """IDs -> users.get -> IDs"""
    fields = config.fields
    if not os.path.isdir(datetime):
        os.makedirs(datetime)
    path = os.path.join(datetime, f"users_info_{iteration}.csv")
    list_of_users = []
    divided_list = numpy.array_split(users_ids, apis.qsize())
    if fields.find('counters') != -1 or fields.find('military') != -1:
        coros = (get_users(ids, True, apis, config, fields) for ids in divided_list)
    else:
        coros = (get_users(ids, False, apis, config, fields) for ids in divided_list)

    if config.is_need_to_reload_tokens:
        await config.reload_tokens(apis)
    for coro in limited_as_completed(coros, apis.qsize()):
        users = await coro
        list_of_users.extend(users)
        await sync_to_async(config.refresh_from_db)()
        if config.is_need_to_reload_tokens:
            await config.reload_tokens(apis)
        config.progress += (progress_chunk / len(divided_list))
        await sync_to_async(config.save)()
    saver(list_of_users, path)
    save_on_server(path)
    os.remove(path)
    return users_ids


async def ids_groups_members_ids(users_ids, apis: Queue, progress_chunk, config):
    """IDs -> groups.get -> groups.getMembers -> IDs"""
    limit_groups = config.limit_groups
    limit_members = config.limit_members
    hard_limit_groups = config.hard_limit_groups
    hard_limit_members = config.hard_limit_members
    ids_of_all_members = []

    async def one_user_all_groups(usr_id):
        groups = await get_groups(usr_id, limit_groups, apis, hard_limit_groups, config)
        ids_of_members = []
        if len(groups) != 0:
            async def one_iteration(group_id):
                one_group_members_ids = await \
                    get_members(group_id, limit_members, apis, hard_limit_members, config)
                ids_of_members.extend(one_group_members_ids)

            for group in groups:
                await one_iteration(group)
        ids_of_all_members.extend(ids_of_members)

    await coros_executor(one_user_all_groups, users_ids, apis, config, progress_chunk)
    return ids_of_all_members


async def ids_friends_ids(users_ids, apis: Queue, progress_chunk, config):
    """IDs -> friends.get -> IDs"""
    ids_of_all_friends = []

    async def one_iteration(usr_id):
        friends_of_one_user = await get_friends(usr_id, apis, config)
        ids_of_all_friends.extend(friends_of_one_user)

    await coros_executor(one_iteration, users_ids, apis, config, progress_chunk)
    return ids_of_all_friends


async def ids_albums_photos_ids(users_ids, apis: Queue, iteration, progress_chunk, config, datetime):
    """IDs -> photos.getAlbums -> photos.get -> IDs"""
    path = os.path.join(datetime, f"photos_{iteration}")
    limit_photos = config.limit_photos
    hard_limit = config.hard_limit_photos
    if not os.path.isdir(path):
        os.makedirs(path)

    async def one_iteration(usr_id):
        albums = await get_albums(usr_id, apis, config)
        await get_photos(usr_id, albums, limit_photos, path, False, apis, hard_limit, config)

    await coros_executor(one_iteration, users_ids, apis, config, progress_chunk)
    return users_ids


async def ids_albums_photos_download_ids(users_ids, apis: Queue, iteration, progress_chunk, config, datetime):
    """IDs -> photos.getAlbums -> photos.get -> Download photos -> IDs"""
    limit_photos = config.limit_photos
    photo_type = config.photo_type
    hard_limit = config.hard_limit_photos
    path = os.path.join(datetime, f"photos_{iteration}")
    if not os.path.isdir(path):
        os.makedirs(path)

    async def one_iteration(usr_id):
        albums = await get_albums(usr_id, apis, config)
        await get_photos(usr_id, albums, limit_photos, path, True, apis, hard_limit, config, photo_type)

    await coros_executor(one_iteration, users_ids, apis, config, progress_chunk)
    return users_ids


async def ids_posts_ids(users_ids, apis: Queue, iteration, progress_chunk, config, datetime):
    """IDs -> wall.get -> IDs"""
    limit_posts = config.limit_posts
    hard_limit_posts = config.hard_limit_posts
    path_with_new_dir = os.path.join(datetime, f"posts_{iteration}")
    if not os.path.isdir(path_with_new_dir):
        os.makedirs(path_with_new_dir)

    async def one_iteration(usr_id):
        ready_path = os.path.join(path_with_new_dir, f"{usr_id}.csv")
        await get_posts(usr_id, limit_posts, ready_path, apis, hard_limit_posts, config)

    await coros_executor(one_iteration, users_ids, apis, config, progress_chunk)
    return users_ids

"""Helpers functions"""
from asyncio import Queue
from datetime import datetime

from vkbottle import API


def all_users_fields():
    """Func returns all available users.get fields"""
    users_fields = ["counters", "is_no_index", "photo_id", "verified", "sex", "bdate", "city", "country",
                    "home_town", "has_photo", "photo_50", "photo_100", "photo_200_orig", "photo_200",
                    "photo_400_orig", "photo_max", "photo_max_orig", "online", "domain", "has_mobile",
                    "contacts", "site", "education", "universities", "schools", "status", "last_seen",
                    "followers_count", "common_count", "occupation", "nickname", "relatives", "relation",
                    "personal", "connections", "exports", "activities", "interests", "music", "movies",
                    "tv", "books", "games", "about", "quotes", "timezone", "screen_name", "maiden_name",
                    "crop_photo", "career", "military"]
    return users_fields


def get_users_fields(request):
    """Func gets request and returns fields separated by comma"""
    fields = ''
    for users_field in all_users_fields():
        if users_field in request.POST:
            fields += users_field + ', '
    return fields


def current_date_and_time():
    """Func returns current date and time in dd-mm-yyyy hh:mm:ss format"""
    now = datetime.now()
    return now.strftime("%d-%m-%Y %H:%M:%S")


async def get_settings(tokens):
    """Func for getting APIs queue by tokens"""
    api_list = [get_api(token) for token in tokens]
    apis = Queue()
    for api in api_list:
        await apis.put(api)
    return apis


def get_api(token):
    """Getting API"""
    api = API(token=token)
    return api


def split_ids(text):
    """Func returns list[str] of IDs"""
    data = str(text).splitlines()
    return data


def chain_interpreter(chain):
    """Func converts the encoded chain into its textual representation"""
    interpreted_chain = ''
    for link in chain:
        if link == "1":
            interpreted_chain += 'IDs -> users.get -> '
        if link == "2":
            interpreted_chain += 'IDs -> groups.get -> groups.getMembers -> '
        if link == "3":
            interpreted_chain += 'IDs -> friends.get -> '
        if link == "4":
            interpreted_chain += 'IDs -> photos.getAlbums -> photos.get (w/o download) -> '
        if link == "5":
            interpreted_chain += 'IDs -> photos.getAlbums -> photos.get (with download) -> '
        if link == "6":
            interpreted_chain += 'IDs -> wall.get -> '
    return interpreted_chain

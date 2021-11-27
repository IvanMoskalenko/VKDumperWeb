"""Helpers functions"""
import asyncio
import sys
from itertools import islice
import httplib2


def get_required_size(sizes, photo_type):
    """Func gets given size of photo."""
    available_types = ['s', 'm', 'x']
    if photo_type in available_types:
        required_size = dict()
        for size in sizes:
            if size['type'] == photo_type:
                required_size = size
        return required_size
    sys.exit('Invalid photo type')


def save_image(url, path):
    """Func downloads image."""
    cash = httplib2.Http('.cache')
    _, content = cash.request(url)
    with open(path, 'wb') as out:
        out.write(content)


def limited_as_completed(coros, limit):
    futures = [
        asyncio.ensure_future(c)
        for c in islice(coros, 0, limit)
    ]

    async def first_to_finish():
        while True:
            await asyncio.sleep(0)
            for f in futures:
                if f.done():
                    futures.remove(f)
                    try:
                        newf = next(coros)
                        futures.append(
                            asyncio.ensure_future(newf))
                    except StopIteration as e:
                        pass
                    return f.result()
    while len(futures) > 0:
        yield first_to_finish()


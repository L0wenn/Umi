import aiohttp


async def get_json(url):
    try:
        async with aiohttp.ClientSession() as client:
            async with client.get(url) as responce:
                res = await responce.json()
    except TypeError:
        return

    return res

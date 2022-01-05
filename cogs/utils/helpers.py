import aiohttp
import discord
import datetime
import os
import aiofiles


async def get_json(url):
    try:
        async with aiohttp.ClientSession() as client:
            async with client.get(url) as response:
                if response.status == 200:
                    res = await response.json()
                    return res
                else:
                    print(f"Unable to get JSON from {url}")
    except TypeError:
        return

async def get_image(bot, ctx, user=None):
        if user:
            if user.is_avatar_animated():
                return str(user.avatar_url_as(format="gif"))
            else:
                return str(user.avatar_url_as(format="png"))

        await ctx.trigger_typing()
        message = ctx.message

        if len(message.attachments) > 0:
            return message.attachments[0].url

        def check(m):
            return m.channel == message.channel and m.author == message.author

        try:
            e = discord.Embed(title=":frame_photo: | Send me an image!", color=bot.color)
            await ctx.send(embed=e)
            x = await bot.wait_for("message", check=check, timeout=15)
        except:
            e = discord.Embed(title=":clock1: | Timed out...", color=bot.color)
            return await ctx.send(embed=e)

        if not len(x.attachments) >= 1:
            e = discord.Embed(title=":x: | No images found...", color=discord.Color.red())
            return await ctx.send(embed=e)

        return x.attachments[0].url
    
async def download_image(url, path):
    img_name = f"{int(datetime.datetime.now().timestamp())}.png"
    path = os.path.join(path, img_name)
    async with aiohttp.ClientSession() as client:
        async with client.get(url) as response:
            if response.status == 200:
                content = await response.read()
                async with aiofiles.open(path, "wb") as f:
                    await f.write(content)
                    return img_name
            else:
                print(f"Unable to download image from {url}")
                
import aiohttp
import discord


async def get_json(url):
    header = {"User-agent": "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0"}
    try:
        async with aiohttp.ClientSession(headers=header) as client:
            async with client.get(url) as responce:
                res = await responce.json()
    except TypeError:
        return

    return res

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
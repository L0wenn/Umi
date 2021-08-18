import asyncio
import discord
from discord.ext import commands
from discord.ext.commands import BucketType
from cogs.utils.helpers import get_json
from random import choice


GELBOORU_URL = "https://middle-gelbooru.herokuapp.com/gelbooru?q={}"

async def get_posts(tags):
    url = GELBOORU_URL.format(tags)
    search = await get_json(url)

    # post = choice(search)
    # image = post["file_url"]

    return search


class NSFW(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(aliases=["gb", "gel"])
    @commands.is_nsfw()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def gelbooru(self, ctx, tags: str = None, amount: int = 1):
        """Returns an image(s) from Gelbooru. NSFW channels only.
        Example of multiple tags: `m!gelbooru mint_(arknights)+solo+rating:safe 10`
        """
        posts = await get_posts(tags)
        if not posts:
            return await ctx.send(embed = discord.Embed(description=f"I couldn't find any images with tag(s) `{tags}`",
            color=discord.Color.red()))

        for i in range(amount):
            post = choice(posts)
            image = post["file_url"]
            await ctx.send(image)
            


    @commands.command()
    @commands.is_nsfw()
    @commands.cooldown(1, 10000000000000000000000000000000, type=BucketType.user)
    async def e621(self, ctx, tags: str = None, amount: int = 1):
        await ctx.send("Nasty furfag. Disgusting")


def setup(bot):
    bot.add_cog(NSFW(bot))
from random import choice
import os

import discord
from discord.ext import commands
from discord.ext.commands import BucketType

from cogs.utils.helpers import get_json as gj


class Reactions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    async def __get_gif(self, search_term):
        key = os.environ.get("TENORAPI") if not self.bot.debug_mode else self.bot.config["tenorAPI"]
        res = await gj("https://api.tenor.com/v1/search?q=%s&key=%s&limit=%s" % (search_term, key, 15))
        obj = choice(res["results"])
        image = obj["media"][0]["gif"]["url"]

        return image


    async def __create_embed(self, text, image):
        e = discord.Embed(description = text)
        e.set_image(url = image)
        e.set_footer(text="GIFs provided by Tenor")
        return e
        

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def hug(self, ctx, user: discord.Member = None):
        if user == None or user == ctx.author:
            text = f"{ctx.author.mention} wants hugs! Come here~"
        else:
            text = f"{ctx.author.mention} has hugged {user.mention}"

        image = await self.__get_gif("anime hug")
        e = await self.__create_embed(text, image)
        await ctx.send(embed = e)


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def cuddle(self, ctx, user: discord.Member = None):
        if user == None or user == ctx.author:
            text = f"Come here, {ctx.author.mention} I'll cuddle you"
        else:
            text = f"{ctx.author.mention} is cuddling {user.mention}. They are so cute~"

        image = await self.__get_gif("anime cuddle")
        e = await self.__create_embed(text, image)
        await ctx.send(embed = e)


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def kiss(self, ctx, user: discord.Member = None):
        if user == None or user == ctx.author:
            text = f"Looks like {ctx.author.mention} is kissing yourself :open_mouth:"
        else:
            text = f"Everyone!!! {ctx.author.mention} is kissing {user.mention}!"

        image = await self.__get_gif("anime kiss")
        e = await self.__create_embed(text, image)
        await ctx.send(embed = e)


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def poke(self, ctx, user: discord.Member = None):
        if user == None or user == ctx.author:
            text = f"*pokes {ctx.author.mention}*"
        else:
            text = f"*{ctx.author.mention} pokes {user.mention}*"

        image = await self.__get_gif("anime poke")
        e = await self.__create_embed(text, image)
        await ctx.send(embed = e)


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def blush(self, ctx, user: discord.Member = None):
        if user == None or user == ctx.author:
            text = f"Look! {ctx.author.mention} is blushing! I wonder why~"
        else:
            text = f"Aww {user.mention} has made {ctx.author.mention} blush"

        image = await self.__get_gif("anime blush")
        e = await self.__create_embed(text, image)
        await ctx.send(embed = e)


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def confused(self, ctx):
        text = f"{ctx.author.mention} looks confused"
        image = await self.__get_gif("anime confused")
        e = await self.__create_embed(text, image)
        await ctx.send(embed = e)


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def lick(self, ctx, user: discord.Member = None):
        if user == None or user == ctx.author:
            text = f"*licks {ctx.author.mention}* Hehe~"
        else:
            text = f"{ctx.author.mention} has licked {user.mention} OwO"

        image = await self.__get_gif("anime lick")
        e = await self.__create_embed(text, image)
        await ctx.send(embed = e)


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def pout(self, ctx, user: discord.Member = None):
        if user == None or user == ctx.author:
            text = f"Why {ctx.author.mention} is pouting?"
        else:
            text = f"{ctx.author.mention} pouts at {user.mention}, something happened?"

        image = await self.__get_gif("anime pout")
        e = await self.__create_embed(text, image)
        await ctx.send(embed = e)


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def slap(self, ctx, user: discord.Member = None):
        if user == None or user == ctx.author:
            text = f"{ctx.author.mention} is slapping yourself... Is that some weird fetish?"
        else:
            text = f"Oof! {ctx.author.mention} has slapped {user.mention}. Hope this wasn't hurt :open_mouth:"

        image = await self.__get_gif("anime slap")
        e = await self.__create_embed(text, image)
        await ctx.send(embed = e)


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def pat(self, ctx, user: discord.Member = None):
        if user == None or user == ctx.author:
            text = f"Pat-pat cute {ctx.author.mention} <3"
        else:
            text = f"{ctx.author.mention} is patting {user.mention} uwu"

        image = await self.__get_gif("anime pat")
        e = await self.__create_embed(text, image)
        await ctx.send(embed = e)

    
    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def smug(self, ctx):
        text = f"{ctx.author.mention} smugs. What do you have on your mind?"
        image = await self.__get_gif("anime smug")
        e = await self.__create_embed(text, image)
        await ctx.send(embed = e)


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def cry(self, ctx, user: discord.Member = None):
        if user == None or user == ctx.author:
            text = f"Shhh, {ctx.author.mention} don't cry"
        else:
            text = f"{user.mention}, how dare you make {ctx.author.mention} cry?!"

        image = await self.__get_gif("anime cry")
        e = await self.__create_embed(text, image)
        await ctx.send(embed = e)


        
def setup(bot):
    bot.add_cog(Reactions(bot))
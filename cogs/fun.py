import asyncio
import json
import random
import os

import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands import BucketType

from cogs.utils import helpers


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def meme(self, ctx):
        """Sends you a random meme from Reddit

        **Usage:** `<prefix>meme`        
        """
        res = await helpers.get_json("https://www.reddit.com/r/memes.json")

        post = random.choice(res["data"]["children"])
        meme = post["data"]

        e = discord.Embed(color=0xFF4500)
        e.set_author(name=f"{meme['title']}", url=f"https://www.reddit.com{meme['permalink']}", icon_url="https://shorturl.at/fmyAN")
        e.set_image(url=meme["url"])

        await ctx.send(embed=e)

    
    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 6, type=BucketType.user)
    async def flipcoin(self, ctx):
        """Flips a coin for you!

        **Usage:** `<prefix>flipcoin`
        """
        coin = random.randint(0, 1)
        e = discord.Embed(title="TAILS!!" if coin == 0 else "HEADS!!", color=self.bot.color)
        e.set_image(url="https://shorturl.at/knEJ4" if coin == 0 else "https://shorturl.at/krAF6")
        await ctx.send(embed=e)


    @commands.command(name="8ball")
    @commands.guild_only()
    @commands.cooldown(1, 6, type=BucketType.user)
    async def eightball(self, ctx):
        """Ask a question to the ball and it'll show you the answer
        
        **Usage:** `<prefix>8ball`
        """
        res = await helpers.get_json("https://nekos.life/api/v2/8ball")
        e = discord.Embed(title=res["response"], color=0x000000)
        e.set_image(url=res["url"])
        await ctx.send(embed=e)


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 6, type=BucketType.user)
    async def fact(self, ctx):
        """Sends you a random fact

        **Usage:** `<prefix>fact`
        """
        res = await helpers.get_json("https://nekos.life/api/v2/fact")
        e = discord.Embed(title=":bookmark: | Random Fact!", description=res["fact"], color=self.bot.color)
        await ctx.send(embed=e)

    
    @commands.command(aliases=["owo"])
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def owoify(self, ctx, *, text=None):
        """OWOifies your text. Cuuuuute
        
        **Usage:** `<prefix>owoify <text>`
        **Aliases:** `owo`
        """
        await ctx.message.delete()
        res = await helpers.get_json(f"https://nekos.life/api/v2/owoify?text={text if text else ''}")
        e = discord.Embed(title="OwO", description=res["owo"] if text else res["msg"], color=self.bot.color)
        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(Fun(bot))

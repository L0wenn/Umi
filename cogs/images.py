import os
from random import choice

import discord
import nekos
from discord.ext import commands
from discord.ext.commands import BucketType

from cogs.utils.helpers import get_json as gj


class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    async def __create_embed(self, text, image):
        e = discord.Embed(description = text)
        e.set_image(url = image)
        e.set_footer(text="Powered by nekos.life")
        return e
        

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def hug(self, ctx, user: discord.Member = None):
        if user == None or user == ctx.author:
            text = f"{ctx.author.mention} wants hugs! Come here~"
        else:
            text = f"{ctx.author.mention} has hugged {user.mention}"

        e = await self.__create_embed(text, nekos.img("hug"))
        await ctx.send(embed = e)


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def cuddle(self, ctx, user: discord.Member = None):
        if user == None or user == ctx.author:
            text = f"Come here, {ctx.author.mention} I'll cuddle you"
        else:
            text = f"Aww {ctx.author.mention} cuddles {user.mention}. So cute~"


        e = await self.__create_embed(text, nekos.img("cuddle"))
        await ctx.send(embed = e)


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def kiss(self, ctx, user: discord.Member = None):
        if user == None or user == ctx.author:
            text = f"Looks like {ctx.author.mention} is kissing yourself :open_mouth:"
        else:
            text = f"{ctx.author.mention} is kissing {user.mention}!"

        e = await self.__create_embed(text, nekos.img("kiss"))
        await ctx.send(embed = e)


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def poke(self, ctx, user: discord.Member = None):
        if user == None or user == ctx.author:
            text = f"*pokes {ctx.author.mention}*"
        else:
            text = f"*{ctx.author.mention} pokes {user.mention}*"

        e = await self.__create_embed(text, nekos.img("poke"))
        await ctx.send(embed = e)


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def slap(self, ctx, user: discord.Member = None):
        if user == None or user == ctx.author:
            text = f"Wait {ctx.author.mention}! Stop slapping yourself!"
        else:
            text = f"Oof! {ctx.author.mention} has slapped {user.mention}. Hope this didn't hurt :open_mouth:"

        e = await self.__create_embed(text, nekos.img("slap"))
        await ctx.send(embed = e)


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def pat(self, ctx, user: discord.Member = None):
        if user == None or user == ctx.author:
            text = f"Pat-pat cute {ctx.author.mention}"
        else:
            text = f"{ctx.author.mention} pats {user.mention}"

        e = await self.__create_embed(text, nekos.img("pat"))
        await ctx.send(embed = e)

    
    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def smug(self, ctx):
        text = f"{ctx.author.mention} smugs. What do you have on your mind?"

        e = await self.__create_embed(text, nekos.img("smug"))
        await ctx.send(embed = e)


    @commands.command(aliases = ["ap"])
    @commands.guild_only()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def avatar_pic(self, ctx):
        """Lets pick you a brand new pfp, shall we?"""
        e = await self.__create_embed(discord.Embed.Empty, nekos.img("avatar"))
        await ctx.send(embed = e)


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def cat(self, ctx):
        """Cats are the best! I mean, this sends you an image of a cat"""
        e = await self.__create_embed("Meow~", nekos.cat())
        await ctx.send(embed = e)


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def neko(self, ctx):
        """Nya?"""
        e = await self.__create_embed("Nya~", nekos.img("neko"))
        await ctx.send(embed = e)
    

        
def setup(bot):
    bot.add_cog(Images(bot))

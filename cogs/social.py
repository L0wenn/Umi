import asyncio
import datetime
import operator

import discord
from discord.ext import commands
from discord.ext.commands import BucketType

from cogs.utils import database as db


class Social(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
            
            
    async def __calculate_place(self, user, server):
        users = []

        userlist = await db.getmany("uID, exp", "levels", f"gID = {server.id}")

        for a in range(len(userlist)):
            try:
                uid = userlist[a][0]
                total_exp = userlist[a][1]
                users.append((uid, total_exp))
            except:
                return "FTGPerr" #failed to get place

        sorted_list = sorted(users, key=operator.itemgetter(1), reverse=True)
 
        rank = 1
        for stats in sorted_list:
            if stats[0] == user.id:
                return rank
            rank += 1


    @commands.command(aliases=["xp", "lvl", "pf"])
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def profile(self, ctx, user: discord.Member = None):
        """Shows your profile. 
        Specify a user to get their profile instead"""
        if user == None:
            user = ctx.author
        if user.bot:
            return

        lvl = await db.get("level", "levels", f"uID = {user.id} AND gID = {ctx.guild.id}")
        exp = await db.get("exp", "levels", f"uID = {user.id} AND gID = {ctx.guild.id}")
        next_level = await db.get("nextLvlExp", "levels", f"uID = {user.id} AND gID = {ctx.guild.id}")
        reps = await db.get("reputation", "global", f"uID = {user.id}")
        place = await self.__calculate_place(user, ctx.guild)
        desc = await db.get("description", "global", f"uID = {user.id}")

        e = discord.Embed(title=f"{user} Profile", description= f":up: | Level: **{lvl} ({exp}/{next_level})**\n" \
                                                                f":chart_with_upwards_trend: | Reputation: **{reps}**\n" \
                                                                f":medal: | Server Place: **{place}**", 
                        color=self.bot.color)
        e.add_field(name="Description", value=f"```{'Beep Boop, description!' if desc == None else desc}```")
        e.set_thumbnail(url=user.avatar_url_as(static_format='png'))
        await ctx.send(embed = e)


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 6, type = BucketType.user)
    async def rep(self, ctx, user: discord.Member):
        """Gives a reputation point to someone"""
        if user.bot:
            return
        if user == ctx.author:
            return

        date = await db.get("repTimeout", "global", f"uID = {ctx.author.id}")
        last_rep = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        dtnow = datetime.datetime.now()
        diff = dtnow - last_rep
        left = datetime.timedelta(hours=23, minutes=59) - diff

        if diff.days == 0:
            s = left.total_seconds()
            h, m = s // 3600, (s % 3600) // 60
            e = discord.Embed(description = f":x: | You can reward a rep point again in `{int(h)}h` and `{int(m)}m`", color = discord.Color.red())
            return await ctx.send(embed = e)

        try:
            await db.update("global", "reputation = reputation + 1", f"uID = {user.id}")
        except:
            e = discord.Embed(title = ":x: | Failed to give a reputation point", color = discord.Color.red())
            return await ctx.send(embed = e)
        
        await db.update("global", 'repTimeout = datetime("now", "localtime")', f"uID = {ctx.author.id}")
        e = discord.Embed(description = f"**:up: | {ctx.author.mention} has given {user.mention} a reputation point**", color = self.bot.color)
        return await ctx.send(embed = e)


    @commands.command(aliases=["lb"], hidden=True)
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def leaderboard(self, ctx):
        """Shows top 10 server level leaderboard."""
        data = await db.getmany("uID, level, exp", "levels", f"gID = {ctx.guild.id} ORDER BY exp DESC LIMIT 10")
        place = await self.__calculate_place(ctx.author, ctx.guild)

        e = discord.Embed(title = ":earth_americas: | Server Leaderboard", color = self.bot.color)
        e.set_footer(text=f"Your place: {place}")
        
        place = 1
        for user in data:
            print(user[0])
            userObj = self.bot.get_user(user[0])
            print(userObj)

            e.add_field(name = f"{place}.{userObj.name}", value = f"LEVEL: {user[1]}\nEXP: {user[2]}")
            place += 1

        return await ctx.send(embed = e)
        

    @commands.command(aliases=["desc"])
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def description(self, ctx, *, text: str = None):
        """Sets description for your profile
        Provide no text in order to reset your description
        """
        if text == None:
            await db.update("global", "description = NULL", f"uID = {ctx.author.id}")

            e = discord.Embed(title = ":page_facing_up: | Your description has been reset successfuly!", color = self.bot.color)
            return await ctx.send(embed=e)

        if len(text) > 125:
            e = discord.Embed(title = ":page_facing_up: | Your description is longer than 125 characters", color = discord.Color.red())
            return await ctx.send(embed=e)

        await db.update("global", f'description = "{text}"', f"uID = {ctx.author.id}")

        e = discord.Embed(title = ":page_facing_up: | Your description has been set!", color = self.bot.color)
        return await ctx.send(embed=e)
        

def setup(bot):
    bot.add_cog(Social(bot))

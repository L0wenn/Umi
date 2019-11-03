import asyncio
import datetime
import math
import operator
from random import randint

import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands import BucketType, Cog

from cogs.utils import database as db


class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
            
            
    async def __calculate_place(self, user, mode, server = None):
        users = []

        if mode == 0: #global
            userlist = await db.getmany("id, exp", "levelsGlobal")
        else: #server
            userlist = await db.getmany("uID, exp", "levelsGuilds", f"gID = {server.id}")

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
        """Shows your global profile. 
        Specify a user to get user's stats instead"""
        if user == None:
            user = ctx.author
        if user.bot:
            return

        lvl = await db.get("level", "levelsGlobal", f"id = {user.id}")
        exp = await db.get("exp", "levelsGlobal", f"id = {user.id}")
        next_level = await db.get("nextLevel", "levelsGlobal", f"id = {user.id}")
        reps = await db.get("reputation", "levelsGlobal", f"id = {user.id}")
        gl_place = await self.__calculate_place(user, 0)
        desc = await db.get("description", "levelsGlobal", f"id = {user.id}")

        e = discord.Embed(title=f"{user} Profile", description= f":earth_americas: | Level: **{lvl} ({exp}/{next_level})**\n" \
                                                                f":chart_with_upwards_trend: | Reputation: **{reps}**\n" \
                                                                f":globe_with_meridians: | Global Place: **{gl_place}**", 
                        color=self.bot.color)
        e.add_field(name="Description", value=f"```{'Beep Boop, description!' if desc == None else desc}```")
        e.set_thumbnail(url=user.avatar_url_as(static_format='png'))
        await ctx.send(embed = e)


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def rank(self, ctx, user: discord.Member = None):
        """Shows your current server profile. 
        Specify a user to get user's stats instead"""
        if user == None:
            user = ctx.author
        if user.bot:
            return

        lvl = await db.get("level", "levelsGuilds", f"uID = {user.id} AND gID = {ctx.guild.id}")
        exp = await db.get("exp", "levelsGuilds", f"uID = {user.id} AND gID = {ctx.guild.id}")
        next_level = await db.get("nextLevel", "levelsGuilds", f"uID = {user.id} AND gID = {ctx.guild.id}")
        s_place = await self.__calculate_place(user, 1, ctx.guild)

        e = discord.Embed(title=f"{user} Server Rank", description= f":one: | Level: **{lvl} ({exp}/{next_level})**\n" \
                                                                f":cityscape: | Server Place: **{s_place}**", 
                        color=self.bot.color)
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

        date = await db.get("lastRep", "levelsGlobal", f"id = {user.id}")
        last_rep = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        dtnow = datetime.datetime.now()
        diff = dtnow - last_rep
        left = datetime.timedelta(hours=23, minutes=59) - diff

        if diff.days == 0:
            s = left.total_seconds()
            h, m = s // 3600, (s % 3600) // 60
            e = discord.Embed(description = f":x: | You can reward a rep point again in `{int(h)}h` and `{int(m)}m`")
            return await ctx.send(embed = e)

        try:
            await db.update("levelsGlobal", "reputation = reputation + 1", f"id = {user.id}")
        except:
            e = discord.Embed(title = ":x: | Failed to give a reputation point", color = discord.Color.red())
            return await ctx.send(embed = e)
        
        await db.update("levelsGlobal", 'lastRep = datetime("now", "localtime")', f"id = {ctx.author.id}")
        e = discord.Embed(description = f"**:up: | {ctx.author.mention} has given {user.mention} a reputation point**", color = self.bot.color)
        return await ctx.send(embed = e)
    

    @commands.command(aliases=["lrr"])
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def lvlrolereward(self, ctx, lvl: int, *, roleName = None):
        """Sets a role on specified level. 
        Provide no role name in order to delete the role reward
        
        **Requires `Manage Roles` permission**
        """
        if roleName == None:
            try:
                await db.delete("levelsRewards", f"gID = {ctx.guild.id} AND level = {lvl}")
            except:
                e = discord.Embed(title = ":x: | There's already no rewards at this level!", color = discord.Color.red())
                return await ctx.send(embed = e)

        try:
            role = discord.utils.get(ctx.guild.roles, name=roleName)
        except:
            e = discord.Embed(title = ":x: | Unable to find the role!", color = discord.Color.red())
            return await ctx.send(embed = e)
        else:
            await db.insert("levelsRewards(gID, rID, level)", f"{ctx.guild.id}, {role.id}, {lvl}")

            e = discord.Embed(description = f":white_check_mark: | Users, who reach __{lvl} level__ will receive `{role.name}` role", color = discord.Color.green())
            return await ctx.send(embed = e)

    
    @commands.command(aliases=["lur"])
    @commands.guild_only()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def lvluprewards(self, ctx, page: int = 1):
        """Shows current level up rewards"""
        start = 0 if page == 1 else page * 10 - 9
        end = page * 10

        data = await db.getmany("rID, level", "levelsRewards", f"gID = {ctx.guild.id} ORDER BY level DESC")
        try:
            check = data[0]
        except IndexError:
            e = discord.Embed(title = ":x: | This server doesn't have rewards yet", color = discord.Color.red())
            return await ctx.send(embed = e)

        total_pages = round(len(data) / 10)
        e = discord.Embed(title = ":up: | Server Rewards", color = self.bot.color)
        e.set_footer(text=f"Page: {page}/{total_pages + 1}")
        for i in range(start, end):
            try:
                role = discord.utils.get(ctx.guild.roles, id = data[i][0])
                e.add_field(name = f"Level {data[i][1]}", value = f"{role.mention} role", inline = False)
            except IndexError:
                pass

        return await ctx.send(embed = e)


    @commands.command(aliases=["ae"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def addexp(self, ctx, user: discord.Member, amount: int):
        """Adds EXP points to specified user.

        This is doesn't affect on global ranking. 
        You also can pass negative values

        **Requires `Administrator` permission**
        """
        try:
            await db.update("levelsGuilds", f"exp = exp + {amount}", f"id = {user.id}")
        except:
            e = discord.Embed(title=":x: | An unknown error occured!", color = discord.Color.red())
            return await ctx.send(embed = e)

        e = discord.Embed(title = f":up: | Added {amount}exp to {user}")
        return await ctx.send(embed = e)


    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def lvlreset(self, ctx, user: discord.Member = None):
        """Resets specified user's LVL or LVL of all users in server
        
        **Requires `Administrator` permission**
        """
        if user == None:
            field = f"gID = {ctx.guild.id}"
            fmt = ":arrows_counterclockwise: | Successfuly reset level for all users!"
        else:
            field = f"uID = {user.id} AND gID = {ctx.guild.id}"
            fmt = f":arrows_counterclockwise: | Successfuly reset level for {user}!"

        e = discord.Embed(title = ":grey_question: | Confirm your action! yes/no", color = discord.Color.orange())
        msg = await ctx.send(embed = e)

        try:
            confirm = await self.bot.wait_for("message", check = lambda m: m.author == ctx.author and m.content.lower() in ["yes", "no"], timeout = 60)
        except asyncio.TimeoutError:
            e = discord.Embed(title = ":clock1: | Timed out...", color = discord.Color.red())
            return await msg.edit(embed = e)
        
        if confirm.content.lower() == "yes":
            await db.update("levelsGuilds", "level = 1", field)
            await db.update("levelsGuilds", "exp = 0", field)
            await db.update("levelsGuilds", "nextLevel = 36", field)

            e = discord.Embed(title = fmt, color = discord.Color.green())
            return await msg.edit(embed = e)
        elif confirm.content.lower() == "no":
            return await msg.delete()


    @commands.command(aliases=["lb"])
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def leaderboard(self, ctx):
        """Shows global level leaderboard."""
        data = await db.getmany("id, level, exp", "levelsGlobal ORDER BY exp DESC LIMIT 10")
        gl_place = await self.__calculate_place(ctx.author, 0)

        e = discord.Embed(title = ":earth_americas: | Global Leaderboard", color = self.bot.color)
        e.set_footer(text=f"Your place: {gl_place}")
        
        place = 1
        for user in data:
            userObj = self.bot.get_user(user[0])

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
            await db.update("levelsGlobal", "description = NULL", f"id = {ctx.author.id}")

            e = discord.Embed(title = ":page_facing_up: | Your description has been reset successfuly!", color = self.bot.color)
            return await ctx.send(embed=e)

        if len(text) > 125:
            e = discord.Embed(title = ":page_facing_up: | Your description is longer than 125 characters", color = discord.Color.red())
            return await ctx.send(embed=e)

        await db.update("levelsGlobal", f'description = "{text}"', f"id = {ctx.author.id}")

        e = discord.Embed(title = ":page_facing_up: | Your description has been set!", color = self.bot.color)
        return await ctx.send(embed=e)
        

def setup(bot):
    bot.add_cog(Leveling(bot))

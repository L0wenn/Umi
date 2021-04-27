import asyncio
import os.path
import sys
from random import randint

import discord
from discord.ext import commands
from discord.ext.commands import Cog

from cogs.utils import database as db


class EventHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lvl_cooldown = list()
        self.cooldown_clean = self.bot.loop.create_task(self.clear_cooldowns())


    async def clear_cooldowns(self):
        while True:
            self.lvl_cooldown.clear()
            await asyncio.sleep(60)

    
    async def __check_existing_user(self, user, guild = None):
        if guild == None:
            predicate = "uID"
            table = "levelsGlobal"
            field = f"uID = {user.id}"
        else:
            predicate = "uID"
            table = "levelsGuilds"
            field = f"uID = {user.id} AND gID = {guild.id}"

        try:
            await db.get(predicate, table, field)
            return True
        except:
            return False


    async def __give_role_rewards(self, user, guild):
        if not await self.__check_existing_user(user, guild):
            return

        level = await db.get("level", "levelsGuilds", f"uID = {user.id} AND gID = {guild.id}")
        reward = await db.getmany("rID", "levelsRewards", f"gID = {guild.id} AND level <= {level}")

        if len(reward) != 0:
            for roleID in reward:
                role = discord.utils.get(guild.roles, name = "Sectarian")

                if role in user.roles:
                    return

                await user.add_roles(role)
                

    async def __leveling_handler(self, user, guild = None):
        if guild == None:
            table = "levelsGlobal(uID, level, exp, nextLvlExp, reputation, description, repTimeout)"
            params = f'{user.id}, 1, 0, 36, 0, NULL, datetime("2000-01-01 00:00:00")'
            fmt_table = "levelsGlobal"
            fmt_field = f"uID = {user.id}"
        else:
            table = "levelsGuilds(uID, gID, level, exp, nextLvlExp)"
            params = f"{user.id}, {guild.id}, 1, 0, 36"
            fmt_table = "levelsGuilds"
            fmt_field = f"uID = {user.id} AND gID = {guild.id}"

        if not await self.__check_existing_user(user, guild):
            await db.insert(table, params)
        if user.id in self.lvl_cooldown:
            return
        
        prev_lvl = await db.get("level", fmt_table, fmt_field)
        prev_exp = await db.get("exp", fmt_table, fmt_field)
        next_level = await db.get("nextLvlExp", fmt_table, fmt_field)

        exp = randint(1, 10)
        await db.update(fmt_table, f"exp = exp + {exp}", fmt_field)
        if guild:
            self.lvl_cooldown.append(user.id)

        if (prev_exp + exp) > next_level:
            await db.update(fmt_table, "level = level + 1", fmt_field)

            new_next_lvl = round(((next_level * 0.4 + next_level) / (prev_lvl + 1)) + next_level)
            await db.update(fmt_table, f"nextLvlExp = {new_next_lvl}", fmt_field)

            if guild == None:
                e = discord.Embed(description=f":tada: | **Congratulations, {user.mention}! You have reached __{prev_lvl + 1} level__!**", color=self.bot.color)
                return e

            #await self.__give_role_rewards(user, guild)
                

    @Cog.listener()
    async def on_ready(self):
        if os.path.isfile("bot/Umi/data/umi.db") == False:
            try:
                await db.create_database()
            except Exception as e:
                sys.exit(f"An error was ecountered while trying to create a database: {e}.\nThe bot will not run without database")

        print("Bot online and ready to work!")
        print("-----------------------------")
        print(f"Running on Python {sys.version[:5]}")
        print(f"discord.py ver: {discord.__version__}")
        print(f"Mode: {'DEV' if self.bot.debug_mode else 'Stable'}")
        print("-----------------------------")


    @Cog.listener()
    async def on_command(self, ctx):
        self.bot.commands_used += 1


    @Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        e = await self.__leveling_handler(message.author)
        await self.__leveling_handler(message.author, message.guild)
        
        try:
            await message.channel.send(embed = e)
        except discord.errors.HTTPException:
            pass

        
    @commands.command(hidden = True)
    @commands.is_owner()
    async def cooldowns(self, ctx):
        await ctx.send(self.lvl_cooldown)


def setup(bot):
    bot.add_cog(EventHandler(bot))

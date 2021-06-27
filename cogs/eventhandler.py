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

    
    async def __check_existing_user(self, user, guild):
        predicate = "uID"
        table = "levels"
        field = f"uID = {user.id} AND gID = {guild.id}"

        try:
            await db.get(predicate, table, field)
            return True
        except:
            return False
                

    async def __leveling_handler(self, user, guild):
        table = "levels(uID, gID, level, exp, nextLvlExp)"
        params = f"{user.id}, {guild.id}, 1, 0, 36"
        fmt_table = "levels"
        fmt_field = f"uID = {user.id} AND gID = {guild.id}"

        if not await self.__check_existing_user(user, guild):
            await db.insert(table, params)
            await db.insert("global(uID, reputation, description, repTimeout)", f'{user.id}, 0, NULL, datetime("now", "localtime")')
        if user.id in self.lvl_cooldown:
            return
        
        prev_lvl = await db.get("level", fmt_table, fmt_field)
        prev_exp = await db.get("exp", fmt_table, fmt_field)
        next_level = await db.get("nextLvlExp", fmt_table, fmt_field)

        exp = randint(1, 10)
        await db.update(fmt_table, f"exp = exp + {exp}", fmt_field)
        
        self.lvl_cooldown.append(user.id)

        if (prev_exp + exp) > next_level:
            await db.update(fmt_table, "level = level + 1", fmt_field)

            new_next_lvl = round(((next_level * 0.4 + next_level) / (prev_lvl + 1)) + next_level)
            await db.update(fmt_table, f"nextLvlExp = {new_next_lvl}", fmt_field)

            # TODO: Move to another better hosting goddamn you
            #e = discord.Embed(description=f":tada: | **Congratulations, {user.mention}! You have reached __{prev_lvl + 1} level__!**", color=self.bot.color)
            return

            
    @Cog.listener()
    async def on_ready(self):
        if os.path.isfile("data/umi.db") == False:
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

        await self.bot.change_presence(activity=discord.Game(name="in the library (m!help)"))


    @Cog.listener()
    async def on_command(self, ctx):
        self.bot.commands_used += 1


    @Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        e = await self.__leveling_handler(message.author, message.guild)
        
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

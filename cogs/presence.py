import discord
from discord.ext import commands
import random
import asyncio


class Presence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.task = self.bot.loop.create_task(self.change_presences())

    
    async def change_presences(self):
        await self.bot.wait_until_ready()
        count = 0

        while not self.bot.is_closed():
            if count > len(self.bot.config["statuses"]):
                count = 0

            status = self.bot.config["statuses"][count]
            await self.bot.change_presence(status = discord.Status.online, activity = discord.Game(status))
            await asyncio.sleep(300)
            count += 1


def setup(bot):
    bot.add_cog(Presence(bot))

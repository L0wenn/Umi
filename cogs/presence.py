import discord
from discord.ext import commands
import random
import asyncio


class Presence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.task = self.bot.loop.create_task(self.change_presences())
        self.count = 0

    
    async def change_presences(self):
        while True:
            if self.count >= len(self.bot.config["statuses"]):
                self.count = 0

            status = self.bot.config["statuses"][self.count]
            await self.bot.change_presence(status = discord.Status.online, activity = discord.Game(status))
            await asyncio.sleep(300)
            self.count += 1


def setup(bot):
    bot.add_cog(Presence(bot))

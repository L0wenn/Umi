import itertools
import time
from datetime import datetime

import discord
from discord.ext import commands
from discord.ext.commands import BucketType

from cogs.utils.help import MyOwnHelp


class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = MyOwnHelp()
        bot.help_command.cog = self

    
    def __get_uptime(self):
        delta_uptime = datetime.utcnow() - self.bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        return f"{days}d, {hours}h, {minutes}m, {seconds}s"

    
    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def ping(self, ctx):
        """Pong!! Shows bot's latency
        
        **Usage: `<prefix>ping`**"""
        start = time.perf_counter()
        e = discord.Embed(title=":ping_pong: | Pong!!", description="Please wait...", color=self.bot.color)
        msg = await ctx.send(embed=e)
        end = time.perf_counter()
        dur = (end - start) * 1000
        e = discord.Embed(title=":ping_pong: | Pong!!", description=f":heartbeat: | `{self.bot.latency*1000:.2f}ms`\n:clock1: | `{dur:.2f}ms`", color=self.bot.color)
        await msg.edit(embed=e)

    
    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def invite(self, ctx):
        """Gives bot's invite link
        
        ***Usage: `<prefix>invite`**"""
        await ctx.send("No invite yet")


    @commands.command()
    @commands.cooldown(1, 12, type=BucketType.user)  
    async def about(self, ctx):
        """Shows the main info about the bot"""
        e = discord.Embed(title=":page_with_curl: | About", color=self.bot.color)
        e.add_field(name="Running On", value="Python 3.6.5")
        e.add_field(name="Main Lib", value=f"discord.py {discord.__version__}")
        e.add_field(name="Owner", value="Løwenn#8437")
        e.add_field(name="Guilds", value=len(self.bot.guilds))
        e.add_field(name="Members", value=f"Total: {len(self.bot.users)}")
        e.add_field(name="Uptime", value=self.__get_uptime())

        await ctx.send(embed=e)

    
def setup(bot):
    bot.add_cog(Core(bot))

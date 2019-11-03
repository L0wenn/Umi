import itertools
import time
from datetime import datetime

import discord
from discord.ext import commands
from discord.ext.commands import BucketType

from cogs.utils.help import MyOwnHelp
from cogs.utils.enums import DiscordStatuses as ds, Logos


class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = MyOwnHelp()
        bot.help_command.cog = self
        self.min_latency = None
        self.max_latency = None

    
    def __get_uptime(self):
        delta_uptime = datetime.utcnow() - self.bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        return f"{days}d {hours}h {minutes}m {seconds}s"


    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def ping(self, ctx):
        """Pong!! Shows bot's latency"""
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
        """Gives bot's invite link"""
        e = discord.Embed(title=":incoming_envelope: | Invite the bot!", description="[Invite with Full permissions](https://bit.ly/2H4OyiP) (recomended)\n" \
                                                                                    "[Invite with Customizable permissions](https://bit.ly/2Z8GbZQ)", 
        color=self.bot.color)
        await ctx.send(embed=e)


    @commands.command()
    @commands.cooldown(1, 12, type=BucketType.user)  
    async def about(self, ctx):
        """Shows the main info about the bot"""
        e = discord.Embed(title=f"{Logos.discord.value} | About", description="Hello! I am Umi! And I'm here to make your server shine~!", color=self.bot.color)
        e.add_field(name="Running On", value=f"Python 3.6.5 {Logos.python.value}")
        e.add_field(name="Main Lib", value=f"discord.py {discord.__version__}")
        e.add_field(name="Bot Version", value=self.bot.config["version"])
        e.add_field(name="Owner", value="Løwenn#8437")
        e.add_field(name="Guilds", value=len(self.bot.guilds))
        e.add_field(name="Users", value=f"{ds.online.value}: {len([user for user in self.bot.get_all_members() if user.status == discord.Status.online])}\n"\
                                        f"{ds.idle.value}: {len([user for user in self.bot.get_all_members() if user.status == discord.Status.idle])}\n"\
                                        f"{ds.dnd.value}: {len([user for user in self.bot.get_all_members() if user.status == discord.Status.dnd])}\n"\
                                        f"{ds.offline.value}: {len([user for user in self.bot.get_all_members() if user.status == discord.Status.offline])}")
        e.add_field(name="Messages Read", value=self.bot.messages_read)
        e.add_field(name="Commands Used", value=self.bot.commands_used)
        e.add_field(name="Uptime", value=self.__get_uptime())
        e.set_thumbnail(url=self.bot.user.avatar_url_as(format="png"))
        await ctx.send(embed=e)


    
def setup(bot):
    bot.add_cog(Core(bot))

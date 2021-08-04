import time
from datetime import datetime

import discord
from discord.ext import commands
from discord.ext.commands import BucketType

from cogs.utils.help import BotHelp


class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = BotHelp()
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
        e = discord.Embed(title=":ping_pong: | Pong!!", description=f":heartbeat: | `{self.bot.latency*1000:.2f}ms`\n:incoming_envelope: | `{dur:.2f}ms`", color=self.bot.color)
        await msg.edit(embed=e)

    
    @commands.command()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def invite(self, ctx):
        """Gives bot's invite link"""
        e = discord.Embed(title=":incoming_envelope: | Invite the bot!", description="[Invite Mint](https://discord.com/oauth2/authorize?client_id=424862035063603202&scope=bot&permissions=2146958839)",
        color=self.bot.color)
        await ctx.send(embed=e)


    @commands.command()
    @commands.cooldown(1, 12, type=BucketType.user)  
    async def about(self, ctx):
        """Shows the main info about the bot"""
        e = discord.Embed(title=f"Mint", color=self.bot.color)
        e.add_field(name="Library", value=f"discord.py {discord.__version__}")
        e.add_field(name="Developer", value="mili_#1208")
        e.add_field(name="Guilds", value=len(self.bot.guilds))
        e.add_field(name="Commands Used", value=self.bot.commands_used)
        e.add_field(name="Uptime", value=self.__get_uptime())
        e.add_field(name="Source Code", value="[GitHub](https://github.com/mili-ae/Mint)")
        e.set_thumbnail(url=self.bot.user.avatar_url_as(format="png"))
        await ctx.send(embed=e)


    
def setup(bot):
    bot.add_cog(Core(bot))

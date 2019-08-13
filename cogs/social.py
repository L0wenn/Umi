import discord
from discord.ext import commands
from discord.ext.commands import BucketType

class Social(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 7, type=BucketType.user)
    async def profile(self, ctx, user: discord.Member = None):
        """Shows your or someones profile"""
        pass
    

def setup(bot):
    bot.add_cog(Social(bot))
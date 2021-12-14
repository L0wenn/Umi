import asyncio
import discord
from discord.ext import commands
import pymongo

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = self.bot.db.settings


    @commands.command(aliases=["cs", "chs"])
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def checksettings(self, ctx):
        """
        Shows current bot settings for your server
        """
        guild = self.settings.find_one({"_id": ctx.guild.id})

        log_channel = discord.utils.get(ctx.guild.text_channels, id = guild["logChannel"])
        mute_role = discord.utils.get(ctx.guild.roles, id = guild["muteRoleID"])
        welcome_channel = discord.utils.get(ctx.guild.text_channels, id = guild["welcomeChannel"])
        warn_action = guild["warnAction"]

        e = discord.Embed(title = f":gear: | Bot settings for {ctx.guild.name}", color = self.bot.color)
        e.add_field(name = "Prefix", value = f"`{guild['prefix']}`", inline = False)
        e.add_field(name = "Log Channel", value = log_channel.mention if log_channel is not None else "None", inline = False)
        e.add_field(name = "Mute Role", value = mute_role.mention if mute_role is not None else "None", inline = False)
        e.add_field(name = "Warns Limit", value = guild["warnLimit"], inline = False)
        e.add_field(name = "Warn Action", value = "Ban" if warn_action == True else "Kick", inline = False)
        e.add_field(name = "Welcome Channel", value = welcome_channel.mention if welcome_channel is not None else "None", inline = False)
        e.add_field(name = "Welcome Text", value = f"```{guild['welcomeMessage']}```", inline = False)

        await ctx.send(embed = e)


    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def prefix(self, ctx, *, prefix: str = None):
        """
        Sets a server prefix. Leave blank to reset it to default
        """
        if not prefix:
            self.settings.update_one(
                {"_id": ctx.guild.id},
                {"$set": {
                    "prefix": "="
                }}
            )
            return await ctx.send(embed = discord.Embed(description = "Server prefix was reset to `=`", color = self.bot.color))
        
        self.settings.update_one(
            {"_id": ctx.guild.id},
            {"$set": {
                "prefix": prefix
            }}
        )
        await ctx.send(embed = discord.Embed(description = f"New server prefix now is: `{prefix}`", color = self.bot.color))

    
    @commands.command(aliases=["lc", "lch"])
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def logchannel(self, ctx, channel: discord.TextChannel = None):
        """
        Enables/Disables logging to a specific channel on your server
        """
        if not channel:
            self.settings.update_one(
                {"_id": ctx.guild.id},
                {"$set": {
                    "logChannel": None
                }}
            )
            return await ctx.send(embed = discord.Embed(description = "Logging has been disabled", color = self.bot.color))
        
        self.settings.update_one(
            {"_id": ctx.guild.id},
            {"$set": {
                "logChannel": channel.id
            }}
        )
        await ctx.send(embed = discord.Embed(description = f"The bot will now send logs to {channel.mention}", color = self.bot.color))


    @commands.command(aliases=["mr"])
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def muterole(self, ctx, role: discord.Role = None):
        """
        Sets a mute role for the bot. Leave blank to reset it to default
        """
        if not role:
            self.settings.update_one(
                {"_id": ctx.guild.id},
                {"$set": {
                    "muteRoleID": None
                }}
            )
            return await ctx.send(embed = discord.Embed(description = "Mute role has been reset. The bot will now be assigning 'Muted' role", color = self.bot.color))
        
        self.settings.update_one(
            {"_id": ctx.guild.id},
            {"$set": {
                "muteRoleID": role.id
            }}
        )
        await ctx.send(embed = discord.Embed(description = f"New mute role `{role.name}` has been set", color = self.bot.color))

        
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def welcome(self, ctx, channel: discord.TextChannel = None):
        """
        Enables/Disables welcome messages to a specific channel on your server
        """
        if not channel:
            self.settings.update_one(
                {"_id": ctx.guild.id},
                {"$set": {
                    "welcomeChannel": None
                }}
            )
            return await ctx.send(embed = discord.Embed(description = "Welcome messages have been disabled", color = self.bot.color))
        
        self.settings.update_one(
            {"_id": ctx.guild.id},
            {"$set": {
                "welcomeChannel": channel.id
            }}
        )
        await ctx.send(embed = discord.Embed(description = f"The bot will now send Welcome messages to {channel.mention}", color = self.bot.color))


    @commands.command(aliases=["wmsg"])
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def welcomemessage(self, ctx, *, message: str = None):
        """
        Sets a welcome message. Leave blank to reset it to default

        `?n` - to include joined users name
        `?@n` - same as above except it mentiones(pings) them
        `?g` - to include the name of your server in your welcome messages

        __Example:__ Welcome to ?g, Dr. ?n
        """
        if not self.settings.find_one({"_id": ctx.guild.id})["welcomeChannel"]:
            return await ctx.send(embed = discord.Embed(description = f"You have Welcome messages disabled. You can enable them with `welcome` function", color = discord.Color.red()))
        if len(message) > 255:
            return await ctx.send(embed = discord.Embed(description = f"Your message can't be more than 255 characters long", color = discord.Color.red()))

        if not message:
            self.settings.update_one(
                {"_id": ctx.guild.id},
                {"$set": {
                    "welcomeMessage": "Welcome to ?g, Dr. ?n"
                }}
            )
            return await ctx.send(embed = discord.Embed(description = "Text for Welcome messages have been reset", color = self.bot.color))
        
        self.settings.update_one(
            {"_id": ctx.guild.id},
            {"$set": {
                "welcomeMessage": message
            }}
        )
        await ctx.send(embed = discord.Embed(description = f"Great! The bot will now welcome users with your new Welcome text", color = self.bot.color))


    @commands.command(aliases=["wa"])
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def warnaction(self, ctx, action: str = False):
        """
        Sets what action bot will make on reaching the limit of warns.
        Users will be __kicked__ by default

        Available actions: `ban`, `kick`
        """
        self.settings.update_one(
            {"_id": ctx.guild.id},
            {"$set": {
                "warnAction": True if action.lower() == "ban" else False
            }}
        )
        await ctx.send(embed = discord.Embed(description = f"Done! Now users will be __**{'banned' if action == 'ban' else 'kicked'}**__ on reaching their warns limit", 
                                            color = self.bot.color))

    
    @commands.command(aliases=["wlim", "wl"])
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def warnlimit(self, ctx, limit: int = 3):
        """
        Sets the limit of warns. 3 by default and 10 available bot's limit
        """
        if limit > 10 and limit < 2:
            return await ctx.send(embed = discord.Embed(title = "You can't set the limit more than 10 or less than 2 warns", color = discord.Color.red()))

        self.settings.update_one(
            {"_id": ctx.guild.id},
            {"$set": {
                "warnLimit": limit
            }}
        )
        await ctx.send(embed = discord.Embed(description = f"Max amount of warns has been changed to `{limit}`", color = self.bot.color))


    @commands.command(aliases=["cbg"])
    @commands.guild_only()
    async def changebackground(self, ctx):
        await ctx.send("WIP")
        
        
    @commands.command(aliases=["ctit"])
    @commands.guild_only()
    async def changetitle(self, ctx):
        await ctx.send("WIP")
        
        
    @commands.command(aliases=["cach"])
    @commands.guild_only()
    async def changeachievements(self, ctx):
        await ctx.send("WIP")


def setup(bot):
    bot.add_cog(Settings(bot))
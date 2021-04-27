import asyncio
import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def __create_thumbnail_embed(self, title, description, color, thumbnail):
        e = discord.Embed(title=title, description=description, color=color)
        e.set_thumbnail(url=thumbnail)
        return e


    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, *, reason=None, delete_message_days=7):
        """Bans a user from the server"""        
        e = discord.Embed(title=":hammer: | You have been banned",
                        description=f"By: {ctx.author.mention}\nWith reason: {reason}",
                        color=self.bot.color)
        await user.send(embed=e)

        await user.ban(reason=reason, delete_message_days=7)
        e = self.__create_thumbnail_embed(title=":hammer: | User Banned",
                                    description=f"Banned: {user.mention}\nBy: {ctx.author.mention}\nReason: {reason}",
                                    color=discord.Color.red(),
                                    thumbnail=user.avatar_url_as(format="png"))
        await ctx.send(embed=e)


    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member, *, reason=None):
        """Kicks a user from the server"""
        e = discord.Embed(title=":boot: | You have been kicked",
                        description=f"By: {ctx.author.mention}\nWith reason: {reason}",
                        color=self.bot.color)
        await user.send(embed=e)

        await user.kick(reason=reason)
        e = self.__create_thumbnail_embed(title=":boot: | User Kicked",
                                    description=f"Kicked: {user.mention}\nBy: {ctx.author.mention}\nReason: {reason}",
                                    color=discord.Color.orange(),
                                    thumbnail=user.avatar_url_as(format="png"))
        await ctx.send(embed=e)

        

        
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, user):
        """Unbans a user"""
        for banned in await ctx.guild.bans():
            if user.lower() == banned[1].name.lower():
                await ctx.guild.unban(user=banned[1], reason=f"Unbanned by {ctx.author}")

                e = discord.Embed(title=":hammer: | User Unbanned",
                                description=f"Unbanned: {banned[1].mention}\nBy: {ctx.author.mention}",
                                color=self.bot.color)
                await ctx.send(embed=e)
                break
        else:
            e = discord.Embed(title=f':x: | I can\'t find the user with nickname "{user}"', color=discord.Color.red())
            await ctx.send(embed=e)



    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def prune(self, ctx, amount: int, user: discord.Member = None):
        """Clears `X` messages. You can define a user to delete only user's messages"""
        if amount > 500 or amount < 0:
            e = discord.Embed(title="Invalid amount. It must be greater than 0 and less than 500", color=discord.Color.red())
            return await ctx.send(embed=e)
        def msgcheck(amsg):
            if user:
                return amsg.author.id == user.id
            return True
        deleted = await ctx.channel.purge(limit=amount, check=msgcheck)
        e = discord.Embed(title=":wastebasket: | Messages Deleted",
                        description=f"Deleted **{len(deleted)}/{amount}** possible messages for you", color=self.bot.color)
        await ctx.send(embed=e, delete_after=10)


    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def roleadd(self, ctx, user:discord.Member, *, rolename):
        """Adds a role to a user"""
        try:
            role = discord.utils.get(ctx.guild.roles, name=rolename)
            if role in user.roles:
                e = discord.Embed(title=":question: | This user already has this role", color=self.bot.color)
                return await ctx.send(embed=e)
            await user.add_roles(role)
        except:
            e = discord.Embed(title=":x: | Can't find your role... maybe misspelled?", color=discord.Color.red())
            await ctx.send(embed=e)

        e = discord.Embed(title="Role added", 
                        description=f"{ctx.author.mention} has given a {role.mention} role to {user.mention}", color=self.bot.color)
        await ctx.send(embed=e)

    
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def roleremove(self, ctx, user:discord.Member, *, rolename):
        """Removes a role from a user""" 
        try:
            role = discord.utils.get(ctx.guild.roles, name=rolename)
            if role not in user.roles:
                e = discord.Embed(title=":question: | This user doesn't have this role", color=self.bot.color)
                return await ctx.send(embed=e)
            await user.remove_roles(role)
        except:
            e = discord.Embed(title=":x: | Can't find your role... maybe misspelled?", color=discord.Color.red())
            await ctx.send(embed=e)

        e = discord.Embed(title="Role removed", 
                        description=f"{ctx.author.mention} has took a {role.mention} role from {user.mention}", color=self.bot.color)
        await ctx.send(embed=e)   


    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def mute(self, ctx, user: discord.Member, time: int = 10, *, reason: str = None):
        """Mute a specified user for some amount of time(in minutes)"""
        try:
            role = discord.utils.get(ctx.guild.roles, name="Muted")
        except:
            e = discord.Embed(title = ":mute: | Error",
                            description = f"I can't find a role named `Muted`...", 
                            color = discord.Color.red())
            await ctx.send(embed = e)
        else:
            if role in user.roles:
                e = discord.Embed(title=":mute: | Mute", description="This user is already muted", color=discord.Color.orange())
                return await ctx.send(embed=e)
            await user.add_roles(role)

            e = discord.Embed(title=":mute: | User muted", 
                            description=f"Muted: {user.mention}\nBy: {ctx.author.mention}\nFor: {time}m\nReason: {reason}", 
                            color=discord.Color.orange())
            await ctx.send(embed=e)
            
            await asyncio.sleep(time * 60)
            await user.remove_roles(role)


    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def unmute(self, ctx, user: discord.Member):
        """Unmutes a user"""
        try:
            role = discord.utils.get(ctx.guild.roles, name="Muted")
        except:
            e = discord.Embed(title = ":mute: | Error",
                            description = f"I can't find a role named `Muted`...", 
                            color = discord.Color.red())
            await ctx.send(embed = e)
        else:
            if role not in user.roles:
                e = discord.Embed(title=":mute: | Mute", description="This user doesn't have mute role already", color=discord.Color.orange())
                return await ctx.send(embed=e)

            await user.remove_roles(role)
            e = discord.Embed(title=":mute: | User unmuted", 
                            description=f"Unmuted: {user.mention}\nBy: {ctx.author.mention}", 
                            color=discord.Color.green())
            await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(Moderation(bot))
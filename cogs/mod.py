import random
import time

import discord
from discord.ext import commands


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = self.bot.db.settings

    def __create_thumbnail_embed(self, title, description, color, thumbnail):
        e = discord.Embed(title=title, description=description, color=color)
        e.set_thumbnail(url=thumbnail)
        return e


    @commands.command(aliases=["hban"])
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def hackban(self, ctx, user: discord.User, *, reason=None):
        """Bans a user that isn't in the server""" 
        await ctx.guild.ban(discord.Object(id=user.id), reason=reason, delete_message_days=7)
        e = self.__create_thumbnail_embed(title=":hammer: | User Banned",
                                    description=f"Banned: {user}\nBy: Dr. {ctx.author.mention}\nReason: {reason}",
                                    color=discord.Color.red(),
                                    thumbnail=user.avatar_url_as(format="png"))
        await ctx.send(embed=e)


    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, *, reason=None):
        """Bans a user from the server"""        
        e = discord.Embed(title=":hammer: | You have been banned",
                        description=f"By: Dr. {ctx.author.mention}\nWith reason: {reason}",
                        color=discord.Color.red())
        await user.send(embed=e)

        await user.ban(reason=reason, delete_message_days=7)
        e = self.__create_thumbnail_embed(title=":hammer: | User Banned",
                                    description=f"Banned: {user.mention}\nBy: Dr. {ctx.author.mention}\nReason: {reason}",
                                    color=discord.Color.red(),
                                    thumbnail=user.avatar_url_as(format="png"))
        await ctx.send(embed=e)


    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member, *, reason=None):
        """Kicks a user from the server"""
        e = discord.Embed(title=":boot: | You have been kicked",
                        description=f"By: Dr. {ctx.author.mention}\nWith reason: {reason}",
                        color=discord.Color.orange())
        await user.send(embed=e)

        await user.kick(reason=reason)
        e = self.__create_thumbnail_embed(title=":boot: | User Kicked",
                                    description=f"Kicked: {user.mention}\nBy: Dr. {ctx.author.mention}\nReason: {reason}",
                                    color=discord.Color.orange(),
                                    thumbnail=user.avatar_url_as(format="png"))
        await ctx.send(embed=e)
        
        
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def bab(self, ctx, user: discord.Member):
        """Bab user (has 1% chance of banning)"""
        bab_question_mark = random.randint(1, 100)
        msg = f"**{ctx.author.name}** babbed **{user.name}**!"
        if bab_question_mark == 1:
            msg = f"**{ctx.author.name}** babbed **{user.name}** way too hard!"
            await ctx.invoke(self.bot.get_command("ban"), user=user, reason="Babbed into oblivion")
            
        await ctx.send(msg)


    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, userID):
        """Unbans a user by ID"""
        member = await self.bot.fetch_user(int(userID))
        await ctx.guild.unban(member)

        e = discord.Embed(description=f':hammer: | {userID} has been unbanned by Dr. {ctx.author.mention}', color=discord.Color.green())
        await ctx.send(embed=e)



    @commands.command(aliases=["purge", "clean"])
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


    @commands.command(aliases=["ra", "ar"])
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, user:discord.Member, *, role: discord.Role):
        """Adds a role to a user. You can pass either role ID or it's name"""
        if role:
            if role in user.roles:
                e = discord.Embed(title=":label: | This user already has this role", color=self.bot.color)
                return await ctx.send(embed=e)

            await user.add_roles(role)
            e = discord.Embed(title=":label: | Role added", 
                        description=f"Dr. {ctx.author.mention} has given {role.mention} role to {user.mention}", color=self.bot.color)
            return await ctx.send(embed=e)

        e = discord.Embed(title=":x: | Can't find your role... maybe misspelled?", color=discord.Color.red())
        await ctx.send(embed=e)

        
    @commands.command(aliases=["rr"])
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def roleremove(self, ctx, user:discord.Member, *, role: discord.Role):
        """Removes a role from a user. You can pass either role ID or it's name""" 
        if role:
            if role not in user.roles:
                e = discord.Embed(title=":label: | This user doesn't have this role", color=self.bot.color)
                return await ctx.send(embed=e)

            await user.remove_roles(role)
            e = discord.Embed(title=":label: | Role removed", 
                        description=f"Dr. {ctx.author.mention} has took {role.mention} role from {user.mention}", color=self.bot.color)
            return await ctx.send(embed=e)

        e = discord.Embed(title=":x: | Can't find your role... maybe misspelled?", color=discord.Color.red())
        await ctx.send(embed=e)  


    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def mute(self, ctx, user: discord.Member, *, reason: str = None):
        """Mute a specified user"""
        if not self.settings.find_one({"_id": ctx.guild.id})["muteRoleID"]:
            return await ctx.send(embed = discord.Embed(title = ":mute: | Error",
                                                        description = f"Sorry, Dr. {ctx.author.display_name}. You don't have a mute role set up for me.",
                                                        color = discord.Color.red()))

        role_id = self.settings.find_one({"_id": ctx.guild.id})["muteRoleID"]
        role = discord.utils.get(ctx.guild.roles, id = role_id)

        if role:
            if role in user.roles:
                e = discord.Embed(title=":mute: | Mute", description="This user is already muted", color=discord.Color.orange())
                return await ctx.send(embed=e)
            
            await user.add_roles(role)
            e = discord.Embed(title=":mute: | User muted", 
                            description=f"Muted: {user.mention}\nBy: Dr. {ctx.author.mention}\nReason: {reason}", 
                            color=discord.Color.orange())
            return await ctx.send(embed=e)

        e = discord.Embed(title = ":mute: | Error",
                        description = f"I can't find any mute role with ID [{role_id}]...", 
                        color = discord.Color.red())
        await ctx.send(embed = e)


    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def unmute(self, ctx, user: discord.Member):
        """Unmutes a user"""
        if not self.settings.find_one({"_id": ctx.guild.id})["muteRoleID"]:
            return await ctx.send(embed = discord.Embed(title = ":mute: | Error",
                                                        description = f"Sorry, Dr. {ctx.author.display_name}. You don't have a mute role set up for me.",
                                                        color = discord.Color.red()))

        role_id = self.settings.find_one({"_id": ctx.guild.id})["muteRoleID"]
        role = discord.utils.get(ctx.guild.roles, id = role_id)

        if role:
            if role not in user.roles:
                e = discord.Embed(title=":mute: | Mute", description="This user is not muted", color=discord.Color.orange())
                return await ctx.send(embed=e)

            await user.remove_roles(role)
            e = discord.Embed(title=":mute: | User unmuted", 
                            description=f"Unmuted: {user.mention}\nBy: Dr. {ctx.author.mention}", 
                            color=discord.Color.green())
            return await ctx.send(embed=e)

        e = discord.Embed(title = ":mute: | Error",
                        description = f"I can't find any mute role with ID [{role_id}]...", 
                        color = discord.Color.red())
        await ctx.send(embed = e)


    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str = None):
        """
        Warns specified user and kicks/bans on reaching the warns limit
        """
        guild = self.bot.db[str(ctx.guild.id)]
        member_warns = guild.find_one({"_id": member.id})["warns"]
        limit = self.settings.find_one({"_id": ctx.guild.id})["warnLimit"]
        action = self.settings.find_one({"_id": ctx.guild.id})["warnAction"]
        
        warn_value = [ctx.author.id, reason]
        member_warns.append(warn_value)

        guild.update_one(
            {"_id": member.id},
            {"$set": {
                "warns": member_warns
            }}
        )

        e = discord.Embed(title = f":pencil: | {member.display_name} warned", color = self.bot.color)
        e.add_field(name = "By", value = f"Dr. {ctx.author.mention}", inline = False)
        e.add_field(name = "Reason", value = reason, inline = False)
        e.set_thumbnail(url = member.avatar_url_as(format="png"))
        e.set_footer(text = f"Total warns for {member.id}: {len(member_warns)}/{limit}")
        await ctx.send(embed = e)

        if len(member_warns) >= limit:
            if action == False:
                return await ctx.invoke(self.bot.get_command("kick"), user = member, reason = f"Exceeded the limit of warns({limit})")
            return await ctx.invoke(self.bot.get_command("ban"), user = member, reason = f"Exceeded the limit of warns({limit})")


    @commands.command(aliases = ["wr"])
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def warnremove(self, ctx, member: discord.Member, index: int):
        """
        Removes a warn from user by warn index
        """
        guild = self.bot.db[str(ctx.guild.id)]
        member_warns = guild.find_one({"_id": member.id})["warns"]
        limit = self.settings.find_one({"_id": ctx.guild.id})["warnLimit"]
        warn_element = member_warns.pop(index - 1)

        guild.update_one(
            {"_id": member.id},
            {"$set": {
                "warns": member_warns
            }}
        )

        original_warn_by = discord.utils.get(ctx.guild.members, id = warn_element[0])

        e = discord.Embed(title = f":pencil: | Warn removed", color = self.bot.color)
        e.add_field(name = "By", value = f"Dr. {ctx.author.mention}", inline = False)
        e.add_field(name = "From", value = f"{member.mention}", inline = False)
        e.add_field(name = "Original warn", value = f"Author: {original_warn_by.mention}\nReason: {warn_element[1]}", inline = False)
        e.set_thumbnail(url = member.avatar_url_as(format="png"))
        e.set_footer(text = f"Total warns for {member.id}: {len(member_warns)}/{limit}")
        await ctx.send(embed = e)


    @commands.command(aliases = ["wlist"])
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def warnlist(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        guild = self.bot.db[str(ctx.guild.id)]
        member_warns = guild.find_one({"_id": member.id})["warns"]

        e = discord.Embed(title = f":page_facing_up: | List of {member.display_name} warns", color = self.bot.color)
        for i in range(len(member_warns)):
            original_warn_by = discord.utils.get(ctx.guild.members, id = member_warns[i][0])
            e.add_field(name = f"{i + 1}. Warn by {original_warn_by.display_name}", value = member_warns[i][1], inline = False)
        await ctx.send(embed = e)

                


def setup(bot):
    bot.add_cog(Moderation(bot))
